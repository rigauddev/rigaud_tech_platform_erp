from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.restaurant.domain.entities import RestaurantTableShape, RestaurantTableStatus


class RestaurantSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class RestaurantFloorRequest(RestaurantSchema):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    description: str | None = Field(default=None, max_length=2000)
    sort_order: int = 0
    is_active: bool = True


class RestaurantFloorResponse(RestaurantSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    code: str
    name: str
    description: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RestaurantTableRequest(RestaurantSchema):
    floor_id: UUID
    number: str = Field(min_length=1, max_length=40)
    name: str | None = Field(default=None, max_length=120)
    capacity: int = Field(default=2, ge=1, le=100)
    position_x: Decimal = Field(default=Decimal(0), ge=0)
    position_y: Decimal = Field(default=Decimal(0), ge=0)
    width: Decimal = Field(default=Decimal(96), gt=0, le=2000)
    height: Decimal = Field(default=Decimal(72), gt=0, le=2000)
    shape: RestaurantTableShape = RestaurantTableShape.SQUARE
    status: RestaurantTableStatus = RestaurantTableStatus.AVAILABLE
    qr_code: str | None = Field(default=None, max_length=160)
    sort_order: int = 0
    is_active: bool = True


class RestaurantTableResponse(RestaurantSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    floor_id: UUID
    number: str
    name: str | None
    capacity: int
    position_x: Decimal
    position_y: Decimal
    width: Decimal
    height: Decimal
    shape: RestaurantTableShape
    status: RestaurantTableStatus
    qr_code: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
