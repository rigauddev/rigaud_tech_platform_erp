from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import (
    InventoryAdjustmentStatus,
    InventoryAdjustmentType,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryReservationStatus,
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
