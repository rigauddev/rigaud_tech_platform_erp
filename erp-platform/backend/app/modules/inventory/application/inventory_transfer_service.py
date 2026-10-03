from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.modules.inventory.application.validators import normalize_quantity
from app.modules.inventory.domain.entities import (
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryTransferStatus,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBranchRequiredError,
    InventoryInsufficientStockError,
    InventoryProductNotFoundError,
    InventoryTransferError,
    InventoryWarehouseNotFoundError,
)
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.models import (
    InventoryMovementModel,
    InventoryTransferModel,
)
from app.modules.inventory.infrastructure.transfer_repositories import (
    SQLAlchemyInventoryTransferRepository,
)
from app.modules.inventory.infrastructure.warehouse_location_repositories import (
    SQLAlchemyWarehouseLocationRepository,
)
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.products.domain.repositories import ProductRepository


@dataclass(frozen=True)
class InventoryTransferCreateInput:
    tenant_id: UUID
    source_branch_id: UUID | None
    source_warehouse_id: UUID
    target_branch_id: UUID
    target_warehouse_id: UUID
    product_id: UUID
    quantity: Decimal
    code: str
    reason: str
    source_location_id: UUID | None = None
    target_location_id: UUID | None = None
    notes: str | None = None
    actor_id: UUID | None = None


class InventoryTransferService:
    def __init__(
        self,
        transfers: SQLAlchemyInventoryTransferRepository,
        inventory: InventoryRepository,
        products: ProductRepository,
        warehouses: SQLAlchemyWarehouseRepository,
        locations: SQLAlchemyWarehouseLocationRepository,
    ) -> None:
        self.transfers = transfers
        self.inventory = inventory
        self.products = products
        self.warehouses = warehouses
        self.locations = locations

    async def create(self, input_data: InventoryTransferCreateInput) -> InventoryTransferModel:
        source_branch_id = self._branch(input_data.source_branch_id)
        code = input_data.code.strip().upper()
        reason = input_data.reason.strip()
        if not 2 <= len(code) <= 40 or not 3 <= len(reason) <= 240:
            raise InventoryTransferError("A valid transfer code and reason are required.")
        if input_data.source_warehouse_id == input_data.target_warehouse_id:
            raise InventoryTransferError("Source and target warehouses must be different.")
        if (
            await self.products.get_by_id(input_data.product_id, tenant_id=input_data.tenant_id)
            is None
        ):
            raise InventoryProductNotFoundError("Product not found.")
        await self._validate_scope(
            tenant_id=input_data.tenant_id,
            branch_id=source_branch_id,
            warehouse_id=input_data.source_warehouse_id,
            location_id=input_data.source_location_id,
        )
        await self._validate_scope(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.target_branch_id,
            warehouse_id=input_data.target_warehouse_id,
            location_id=input_data.target_location_id,
        )
        return await self.transfers.add(
            InventoryTransferModel(
                id=uuid4(),
                tenant_id=input_data.tenant_id,
                code=code,
                product_id=input_data.product_id,
                source_branch_id=source_branch_id,
                source_warehouse_id=input_data.source_warehouse_id,
                source_location_id=input_data.source_location_id,
                target_branch_id=input_data.target_branch_id,
                target_warehouse_id=input_data.target_warehouse_id,
                target_location_id=input_data.target_location_id,
                quantity=normalize_quantity(input_data.quantity),
                status=InventoryTransferStatus.REQUESTED,
                reason=reason,
                notes=input_data.notes.strip() if input_data.notes else None,
                created_by=input_data.actor_id,
                updated_by=input_data.actor_id,
            )
        )

    async def dispatch(
        self,
        transfer_id: UUID,
        *,
        tenant_id: UUID,
        active_branch_id: UUID | None,
        actor_id: UUID | None,
    ) -> InventoryTransferModel:
        transfer = await self._get_for_source(transfer_id, tenant_id, active_branch_id)
        if transfer.status != InventoryTransferStatus.REQUESTED:
            raise InventoryTransferError("Only requested transfers can be dispatched.")
        balance = await self.inventory.get_balance(
            tenant_id=tenant_id,
            branch_id=transfer.source_branch_id,
            product_id=transfer.product_id,
            warehouse_id=transfer.source_warehouse_id,
            location_id=transfer.source_location_id,
        )
        if balance is None or balance.available_quantity < transfer.quantity:
            raise InventoryInsufficientStockError("Insufficient available stock for transfer.")
        balance.physical_quantity -= transfer.quantity
        balance.updated_by = actor_id
        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=tenant_id,
                branch_id=transfer.source_branch_id,
                product_id=transfer.product_id,
                warehouse_id=transfer.source_warehouse_id,
                location_id=transfer.source_location_id,
                movement_type=InventoryMovementType.TRANSFER_OUT,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=-transfer.quantity,
                reserved_quantity_delta=Decimal("0.000"),
                putaway_pending_quantity_delta=Decimal("0.000"),
                reason=transfer.reason,
                source_module="inventory_transfer",
                source_id=transfer.id,
                origin_module="TRANSFER",
                business_process="TRANSFER",
                event_name="inventory.transfer.dispatched",
                actor_id=actor_id,
            )
        )
        await self.inventory.add_balance(balance)
        transfer.outbound_movement_id = movement.id
        transfer.status = InventoryTransferStatus.IN_TRANSIT
        transfer.dispatched_at = datetime.now(UTC)
        transfer.updated_by = actor_id
        return await self.transfers.add(transfer)

    async def receive(
        self,
        transfer_id: UUID,
        *,
        tenant_id: UUID,
        active_branch_id: UUID | None,
        actor_id: UUID | None,
    ) -> InventoryTransferModel:
        transfer = await self._get_for_target(transfer_id, tenant_id, active_branch_id)
        if transfer.status != InventoryTransferStatus.IN_TRANSIT:
            raise InventoryTransferError("Only transfers in transit can be received.")
        balance = await self.inventory.get_or_create_balance(
            tenant_id=tenant_id,
            branch_id=transfer.target_branch_id,
            product_id=transfer.product_id,
            warehouse_id=transfer.target_warehouse_id,
            location_id=transfer.target_location_id,
        )
        balance.physical_quantity += transfer.quantity
        balance.updated_by = actor_id
        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=tenant_id,
                branch_id=transfer.target_branch_id,
                product_id=transfer.product_id,
                warehouse_id=transfer.target_warehouse_id,
                location_id=transfer.target_location_id,
                movement_type=InventoryMovementType.TRANSFER_IN,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=transfer.quantity,
                reserved_quantity_delta=Decimal("0.000"),
                putaway_pending_quantity_delta=Decimal("0.000"),
                reason=transfer.reason,
                source_module="inventory_transfer",
                source_id=transfer.id,
                origin_module="TRANSFER",
                business_process="TRANSFER",
                event_name="inventory.transfer.received",
                actor_id=actor_id,
            )
        )
        await self.inventory.add_balance(balance)
        transfer.inbound_movement_id = movement.id
        transfer.status = InventoryTransferStatus.RECEIVED
        transfer.received_at = datetime.now(UTC)
        transfer.updated_by = actor_id
        return await self.transfers.add(transfer)

    async def cancel(
        self,
        transfer_id: UUID,
        *,
        tenant_id: UUID,
        active_branch_id: UUID | None,
        actor_id: UUID | None,
    ) -> InventoryTransferModel:
        transfer = await self._get_for_source(transfer_id, tenant_id, active_branch_id)
        if transfer.status not in {
            InventoryTransferStatus.DRAFT,
            InventoryTransferStatus.REQUESTED,
        }:
            raise InventoryTransferError("Only unshipped transfers can be cancelled.")
        transfer.status = InventoryTransferStatus.CANCELLED
        transfer.cancelled_at = datetime.now(UTC)
        transfer.updated_by = actor_id
        return await self.transfers.add(transfer)

    async def _get_for_source(
        self, transfer_id: UUID, tenant_id: UUID, active_branch_id: UUID | None
    ) -> InventoryTransferModel:
        transfer = await self._get(transfer_id, tenant_id)
        if transfer.source_branch_id != self._branch(active_branch_id):
            raise InventoryTransferError("Transfer is not available in the active source branch.")
        return transfer

    async def _get_for_target(
        self, transfer_id: UUID, tenant_id: UUID, active_branch_id: UUID | None
    ) -> InventoryTransferModel:
        transfer = await self._get(transfer_id, tenant_id)
        if transfer.target_branch_id != self._branch(active_branch_id):
            raise InventoryTransferError("Transfer is not available in the active target branch.")
        return transfer

    async def _get(self, transfer_id: UUID, tenant_id: UUID) -> InventoryTransferModel:
        transfer = await self.transfers.get_by_id(transfer_id, tenant_id=tenant_id)
        if transfer is None:
            raise InventoryTransferError("Inventory transfer not found.")
        return transfer

    async def _validate_scope(
        self, *, tenant_id: UUID, branch_id: UUID, warehouse_id: UUID, location_id: UUID | None
    ) -> None:
        warehouse = await self.warehouses.get_by_id(warehouse_id, tenant_id=tenant_id)
        if warehouse is None or warehouse.branch_id != branch_id or not warehouse.is_active:
            raise InventoryWarehouseNotFoundError("Warehouse not found for branch.")
        if location_id is not None:
            location = await self.locations.get_by_id(location_id, tenant_id=tenant_id)
            if (
                location is None
                or location.branch_id != branch_id
                or location.warehouse_id != warehouse_id
                or not location.is_active
            ):
                raise InventoryTransferError("Location does not belong to the transfer warehouse.")

    @staticmethod
    def _branch(branch_id: UUID | None) -> UUID:
        if branch_id is None:
            raise InventoryBranchRequiredError("Active branch is required.")
        return branch_id
