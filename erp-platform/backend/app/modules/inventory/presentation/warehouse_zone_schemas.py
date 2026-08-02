from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import WarehouseZoneStatus, WarehouseZoneType


class WarehouseZoneBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WarehouseZoneCreateRequest(WarehouseZoneBaseSchema):
    warehouse_id: UUID
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    type: WarehouseZoneType = WarehouseZoneType.STORAGE
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=80)
    sort_order: int = Field(default=0, ge=0, le=9999)
    is_receiving: bool = False
    is_shipping: bool = False
    is_storage: bool = True
    is_production: bool = False
    is_quarantine: bool = False
    is_active: bool = True


class WarehouseZoneUpdateRequest(WarehouseZoneBaseSchema):
    code: str | None = Field(default=None, min_length=2, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    type: WarehouseZoneType | None = None
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=80)
    sort_order: int | None = Field(default=None, ge=0, le=9999)
    is_receiving: bool | None = None
    is_shipping: bool | None = None
    is_storage: bool | None = None
    is_production: bool | None = None
    is_quarantine: bool | None = None
    is_active: bool | None = None


class WarehouseZoneReorderRequest(WarehouseZoneBaseSchema):
    sort_order: int = Field(ge=0, le=9999)


class WarehouseZoneResponse(WarehouseZoneBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    warehouse_id: UUID
    code: str
    name: str
    description: str | None
    type: WarehouseZoneType
    color: str | None
    icon: str | None
    sort_order: int
    is_receiving: bool
    is_shipping: bool
    is_storage: bool
    is_production: bool
    is_quarantine: bool
    status: WarehouseZoneStatus
    is_active: bool
    created_at: datetime
    updated_at: datetime
