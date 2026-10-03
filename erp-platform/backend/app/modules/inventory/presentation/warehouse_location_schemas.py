from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import WarehouseLocationStatus


class WarehouseLocationBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WarehouseLocationCreateRequest(WarehouseLocationBaseSchema):
    warehouse_id: UUID
    zone_id: UUID
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    alias: str | None = Field(default=None, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    qr_code: str | None = Field(default=None, max_length=160)
    aisle: str | None = Field(default=None, max_length=40)
    rack: str | None = Field(default=None, max_length=40)
    shelf: str | None = Field(default=None, max_length=40)
    level: str | None = Field(default=None, max_length=40)
    position: str | None = Field(default=None, max_length=40)
    capacity: Decimal | None = Field(default=None, ge=0)
    capacity_unit: str | None = Field(default=None, max_length=20)
    allow_negative: bool = False
    allow_mixed_items: bool = True
    allow_expired: bool = False
    is_pick_location: bool = False
    is_receive_location: bool = False
    is_shipping_location: bool = False
    is_default: bool = False
    sort_order: int = Field(default=0, ge=0, le=9999)
    is_active: bool = True


class WarehouseLocationUpdateRequest(WarehouseLocationBaseSchema):
    code: str | None = Field(default=None, min_length=2, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    alias: str | None = Field(default=None, max_length=80)
    barcode: str | None = Field(default=None, max_length=80)
    qr_code: str | None = Field(default=None, max_length=160)
    aisle: str | None = Field(default=None, max_length=40)
    rack: str | None = Field(default=None, max_length=40)
    shelf: str | None = Field(default=None, max_length=40)
    level: str | None = Field(default=None, max_length=40)
    position: str | None = Field(default=None, max_length=40)
    capacity: Decimal | None = Field(default=None, ge=0)
    capacity_unit: str | None = Field(default=None, max_length=20)
    allow_negative: bool | None = None
    allow_mixed_items: bool | None = None
    allow_expired: bool | None = None
    is_pick_location: bool | None = None
    is_receive_location: bool | None = None
    is_shipping_location: bool | None = None
    is_default: bool | None = None
    sort_order: int | None = Field(default=None, ge=0, le=9999)
    is_active: bool | None = None


class WarehouseLocationReorderRequest(WarehouseLocationBaseSchema):
    sort_order: int = Field(ge=0, le=9999)


class WarehouseLocationResponse(WarehouseLocationBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    zone_id: UUID
    code: str
    name: str
    alias: str | None
    barcode: str | None
    qr_code: str | None
    aisle: str | None
    rack: str | None
    shelf: str | None
    level: str | None
    position: str | None
    capacity: Decimal | None
    capacity_unit: str | None
    allow_negative: bool
    allow_mixed_items: bool
    allow_expired: bool
    is_pick_location: bool
    is_receive_location: bool
    is_shipping_location: bool
    is_default: bool
    sort_order: int
    status: WarehouseLocationStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
