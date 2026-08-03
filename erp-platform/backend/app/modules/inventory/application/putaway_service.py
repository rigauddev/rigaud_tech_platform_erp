from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.modules.inventory.application.validators import normalize_optional_receiving_text
from app.modules.inventory.domain.entities import (
    InventoryMovementStatus,
    InventoryMovementType,
    ReceivingDocumentStatus,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBalanceNotFoundError,
    InventoryInvalidQuantityError,
    PutAwayCannotConfirmError,
    ReceivingDocumentNotFoundError,
    WarehouseBranchRequiredError,
    WarehouseLocationBranchRequiredError,
    WarehouseLocationNotFoundError,
)
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.warehouse_location_repositories import (
    WarehouseLocationRepository,
)
from app.modules.inventory.infrastructure.models import (
    InventoryBalanceModel,
    InventoryMovementModel,
    ReceivingDocumentModel,
)


@dataclass(frozen=True)
class PutAwayInput:
    tenant_id: UUID
    branch_id: UUID | None
    document_id: UUID
    product_id: UUID
    location_id: UUID
    quantity: Decimal
    reason: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class PutAwayResult:
    document: ReceivingDocumentModel
    source_balance: InventoryBalanceModel
    target_balance: InventoryBalanceModel
    movement: InventoryMovementModel


class PutAwayService:
    def __init__(
        self,
        receiving: ReceivingDocumentRepository,
        inventory: InventoryRepository,
        locations: WarehouseLocationRepository,
    ) -> None:
        self.receiving = receiving
        self.inventory = inventory
        self.locations = locations

    async def confirm(self, input_data: PutAwayInput) -> PutAwayResult:
        if input_data.branch_id is None:
            raise PutAwayCannotConfirmError("Active branch is required.")
        if input_data.quantity <= 0:
            raise InventoryInvalidQuantityError("Quantity must be greater than zero.")

        document = await self.receiving.get_by_id(
            input_data.document_id,
            tenant_id=input_data.tenant_id,
        )
        if document is None:
            raise ReceivingDocumentNotFoundError("Receiving document not found.")
        if document.branch_id != input_data.branch_id:
            raise WarehouseBranchRequiredError("Receiving document belongs to another branch.")
        if document.status != ReceivingDocumentStatus.PUTAWAY_PENDING:
            raise PutAwayCannotConfirmError("Receiving document is not pending put away.")

        location = await self.locations.get_by_id(
            input_data.location_id,
            tenant_id=input_data.tenant_id,
        )
        if location is None:
            raise WarehouseLocationNotFoundError("Warehouse location not found.")
        if location.branch_id != input_data.branch_id:
            raise WarehouseLocationBranchRequiredError("Location belongs to another branch.")
        if location.warehouse_id != document.warehouse_id:
            raise PutAwayCannotConfirmError("Location belongs to another warehouse.")
        if not location.is_active:
            raise PutAwayCannotConfirmError("Warehouse location is inactive.")

        item = next(
            (item for item in document.items if item.product_id == input_data.product_id),
            None,
        )
        if item is None:
            raise PutAwayCannotConfirmError("Product is not part of the receiving document.")
        if input_data.quantity > item.received_quantity:
            raise InventoryInvalidQuantityError("Quantity cannot exceed received quantity.")

        source_balance = await self.inventory.get_balance(
            tenant_id=input_data.tenant_id,
            branch_id=document.branch_id,
            product_id=input_data.product_id,
            warehouse_id=document.warehouse_id,
            location_id=None,
        )
        if source_balance is None:
            raise InventoryBalanceNotFoundError("Put away pending balance not found.")
        if source_balance.putaway_pending_quantity < input_data.quantity:
            raise PutAwayCannotConfirmError("Insufficient pending put away quantity.")

        reason = f"Put away {document.document_number}"
        if input_data.reason:
            reason = (
                normalize_optional_receiving_text(
                    input_data.reason,
                    "reason",
                    max_length=240,
                )
                or reason
            )

        source_balance.physical_quantity -= input_data.quantity
        source_balance.putaway_pending_quantity -= input_data.quantity
        source_balance.updated_by = input_data.actor_id

        target_balance = await self.inventory.get_or_create_balance(
            tenant_id=input_data.tenant_id,
            branch_id=document.branch_id,
            product_id=input_data.product_id,
            warehouse_id=document.warehouse_id,
            location_id=input_data.location_id,
        )
        target_balance.physical_quantity += input_data.quantity
        target_balance.updated_by = input_data.actor_id

        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=input_data.tenant_id,
                branch_id=document.branch_id,
                product_id=input_data.product_id,
                warehouse_id=document.warehouse_id,
                location_id=input_data.location_id,
                movement_type=InventoryMovementType.PUTAWAY,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=Decimal("0.000"),
                reserved_quantity_delta=Decimal("0.000"),
                putaway_pending_quantity_delta=-input_data.quantity,
                reason=reason,
                source_module="receiving",
                source_id=document.id,
                origin_module="PURCHASE",
                business_process="PUTAWAY",
                event_name="inventory.putaway.confirmed",
                actor_id=input_data.actor_id,
            )
        )
        await self.inventory.add_balance(source_balance)
        await self.inventory.add_balance(target_balance)

        if source_balance.putaway_pending_quantity == 0:
            document.status = ReceivingDocumentStatus.AVAILABLE
            document.updated_by = input_data.actor_id
            await self.receiving.add(document)

        return PutAwayResult(
            document=document,
            source_balance=source_balance,
            target_balance=target_balance,
            movement=movement,
        )
