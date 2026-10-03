from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import (
    InventoryAdjustmentReason,
    InventoryAdjustmentStatus,
    InventoryAdjustmentType,
    InventoryCountStatus,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryReservationStatus,
    InventoryTransferStatus,
)


class InventoryBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InventoryAdjustmentRequest(InventoryBaseSchema):
    product_id: UUID
    adjustment_type: InventoryAdjustmentType
    quantity: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=240)
    warehouse_id: UUID | None = None
    location_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)
    reason_code: InventoryAdjustmentReason = InventoryAdjustmentReason.CORRECTION


class InventoryAdjustmentReverseRequest(InventoryBaseSchema):
    reason: str = Field(min_length=3, max_length=240)


class InventoryReservationRequest(InventoryBaseSchema):
    product_id: UUID
    quantity: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=240)
    warehouse_id: UUID | None = None
    location_id: UUID | None = None
    source_module: str | None = Field(default=None, max_length=80)
    source_id: UUID | None = None


class PutAwayConfirmRequest(InventoryBaseSchema):
    document_id: UUID
    product_id: UUID
    location_id: UUID
    quantity: Decimal = Field(gt=0)
    reason: str | None = Field(default=None, max_length=240)


class InventoryCountCreateRequest(InventoryBaseSchema):
    warehouse_id: UUID
    code: str = Field(min_length=2, max_length=40)
    product_ids: list[UUID] = Field(min_length=1, max_length=500)
    location_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class InventoryCountItemQuantityRequest(InventoryBaseSchema):
    counted_quantity: Decimal = Field(ge=0)


class InventoryTransferCreateRequest(InventoryBaseSchema):
    code: str = Field(min_length=2, max_length=40)
    product_id: UUID
    source_warehouse_id: UUID
    target_branch_id: UUID
    target_warehouse_id: UUID
    quantity: Decimal = Field(gt=0)
    reason: str = Field(min_length=3, max_length=240)
    source_location_id: UUID | None = None
    target_location_id: UUID | None = None
    notes: str | None = Field(default=None, max_length=2000)


class InventoryBalanceResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    product_id: UUID
    warehouse_id: UUID | None
    location_id: UUID | None
    physical_quantity: Decimal
    reserved_quantity: Decimal
    putaway_pending_quantity: Decimal
    available_quantity: Decimal
    created_at: datetime
    updated_at: datetime


class InventoryMovementResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    product_id: UUID
    warehouse_id: UUID | None
    location_id: UUID | None
    movement_type: InventoryMovementType
    status: InventoryMovementStatus
    physical_quantity_delta: Decimal
    reserved_quantity_delta: Decimal
    putaway_pending_quantity_delta: Decimal
    reason: str
    source_module: str | None
    source_id: UUID | None
    origin_module: str
    business_process: str
    event_name: str
    actor_id: UUID | None
    immutable: bool = True
    created_at: datetime
    updated_at: datetime


class InventoryAdjustmentResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    product_id: UUID
    movement_id: UUID | None
    warehouse_id: UUID | None
    location_id: UUID | None
    adjustment_type: InventoryAdjustmentType
    status: InventoryAdjustmentStatus
    quantity: Decimal
    reason: str
    notes: str | None
    reason_code: InventoryAdjustmentReason
    reversal_of_id: UUID | None
    created_at: datetime
    updated_at: datetime


class InventoryReservationResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    product_id: UUID
    warehouse_id: UUID | None
    location_id: UUID | None
    status: InventoryReservationStatus
    quantity: Decimal
    reason: str
    source_module: str | None
    source_id: UUID | None
    created_at: datetime
    updated_at: datetime


class InventoryOperationResponse(InventoryBaseSchema):
    balance: InventoryBalanceResponse
    movement: InventoryMovementResponse
    adjustment: InventoryAdjustmentResponse | None = None
    reservation: InventoryReservationResponse | None = None


class InventoryCountItemResponse(InventoryBaseSchema):
    id: UUID
    product_id: UUID
    expected_quantity: Decimal
    counted_quantity: Decimal | None
    divergence_quantity: Decimal | None
    adjustment_movement_id: UUID | None


class InventoryCountResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    location_id: UUID | None
    code: str
    status: InventoryCountStatus
    notes: str | None
    started_at: datetime | None
    finished_at: datetime | None
    items: list[InventoryCountItemResponse]
    created_at: datetime
    updated_at: datetime


class InventoryTransferResponse(InventoryBaseSchema):
    id: UUID
    tenant_id: UUID
    code: str
    product_id: UUID
    source_branch_id: UUID
    source_warehouse_id: UUID
    source_location_id: UUID | None
    target_branch_id: UUID
    target_warehouse_id: UUID
    target_location_id: UUID | None
    quantity: Decimal
    status: InventoryTransferStatus
    reason: str
    notes: str | None
    outbound_movement_id: UUID | None
    inbound_movement_id: UUID | None
    dispatched_at: datetime | None
    received_at: datetime | None
    cancelled_at: datetime | None
    created_at: datetime
    updated_at: datetime
