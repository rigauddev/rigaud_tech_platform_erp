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
    ReceivingDocumentCannotConfirmError,
    ReceivingDocumentNotFoundError,
    WarehouseBranchRequiredError,
    WarehouseInactiveError,
    WarehouseNotFoundError,
)
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import (
    InventoryBalanceModel,
    InventoryMovementModel,
    ReceivingDocumentModel,
)


@dataclass(frozen=True)
class GoodsReceiptInput:
    tenant_id: UUID
    branch_id: UUID | None
    document_id: UUID
    notes: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class GoodsReceiptResult:
    document: ReceivingDocumentModel
    balances: list[InventoryBalanceModel]
    movements: list[InventoryMovementModel]


class GoodsReceiptService:
    def __init__(
        self,
        receiving: ReceivingDocumentRepository,
        inventory: InventoryRepository,
        warehouses: WarehouseRepository,
    ) -> None:
        self.receiving = receiving
        self.inventory = inventory
        self.warehouses = warehouses

    async def confirm(self, input_data: GoodsReceiptInput) -> GoodsReceiptResult:
        if input_data.branch_id is None:
            raise ReceivingDocumentCannotConfirmError("Active branch is required.")
        document = await self.receiving.get_by_id(
            input_data.document_id,
            tenant_id=input_data.tenant_id,
        )
        if document is None:
            raise ReceivingDocumentNotFoundError("Receiving document not found.")
        if document.branch_id != input_data.branch_id:
            raise WarehouseBranchRequiredError("Receiving document belongs to another branch.")
        if document.status in {
            ReceivingDocumentStatus.RECEIVED,
            ReceivingDocumentStatus.PUTAWAY_PENDING,
            ReceivingDocumentStatus.CANCELLED,
        }:
            raise ReceivingDocumentCannotConfirmError(
                "Receiving document cannot be confirmed in its current status."
            )
        warehouse = await self.warehouses.get_by_id(
            document.warehouse_id,
            tenant_id=input_data.tenant_id,
        )
        if warehouse is None:
            raise WarehouseNotFoundError("Warehouse not found.")
        if warehouse.branch_id != input_data.branch_id:
            raise WarehouseBranchRequiredError("Warehouse belongs to another branch.")
        if not warehouse.is_active:
            raise WarehouseInactiveError("Warehouse is inactive.")

        reason = f"Goods receipt {document.document_number}"
        if input_data.notes:
            reason = (
                normalize_optional_receiving_text(
                    input_data.notes,
                    "notes",
                    max_length=240,
                )
                or reason
            )

        balances: list[InventoryBalanceModel] = []
        movements: list[InventoryMovementModel] = []
        for item in document.items:
            if item.received_quantity <= 0:
                continue
            balance = await self.inventory.get_or_create_balance(
                tenant_id=input_data.tenant_id,
                branch_id=document.branch_id,
                product_id=item.product_id,
                warehouse_id=document.warehouse_id,
                location_id=None,
            )
            balance.physical_quantity += item.received_quantity
            balance.putaway_pending_quantity += item.received_quantity
            balance.updated_by = input_data.actor_id
            movement = await self.inventory.add_movement(
                InventoryMovementModel(
                    tenant_id=input_data.tenant_id,
                    branch_id=document.branch_id,
                    product_id=item.product_id,
                    warehouse_id=document.warehouse_id,
                    location_id=None,
                    movement_type=InventoryMovementType.RECEIPT,
                    status=InventoryMovementStatus.CONFIRMED,
                    physical_quantity_delta=item.received_quantity,
                    reserved_quantity_delta=Decimal("0.000"),
                    putaway_pending_quantity_delta=item.received_quantity,
                    reason=reason,
                    source_module="receiving",
                    source_id=document.id,
                    event_name="inventory.receipt.confirmed",
                    actor_id=input_data.actor_id,
                )
            )
            await self.inventory.add_balance(balance)
            balances.append(balance)
            movements.append(movement)

        if not movements:
            raise ReceivingDocumentCannotConfirmError(
                "Receiving document has no received quantity to confirm."
            )

        document.status = ReceivingDocumentStatus.PUTAWAY_PENDING
        document.updated_by = input_data.actor_id
        await self.receiving.add(document)
        return GoodsReceiptResult(document=document, balances=balances, movements=movements)
