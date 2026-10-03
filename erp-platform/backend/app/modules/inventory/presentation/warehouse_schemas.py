from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.inventory.domain.entities import WarehouseStatus


class WarehouseBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WarehouseCreateRequest(WarehouseBaseSchema):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=500)
    is_default: bool = False
    is_active: bool = True


class WarehouseUpdateRequest(WarehouseBaseSchema):
    code: str | None = Field(default=None, min_length=2, max_length=40)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    address: str | None = Field(default=None, max_length=500)
    is_default: bool | None = None
    is_active: bool | None = None


class WarehouseResponse(WarehouseBaseSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    code: str
    name: str
    description: str | None
    address: str | None
    status: WarehouseStatus
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
