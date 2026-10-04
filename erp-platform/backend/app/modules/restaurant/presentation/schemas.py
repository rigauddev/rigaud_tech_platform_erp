from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.restaurant.domain.entities import (
    RestaurantMenuAvailabilityStatus,
    RestaurantSectorType,
    RestaurantStaffRole,
    RestaurantStaffStatus,
    RestaurantTableShape,
    RestaurantTableStatus,
)


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


class RestaurantSectorRequest(RestaurantSchema):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    type: RestaurantSectorType = RestaurantSectorType.DINING_ROOM
    floor_id: UUID | None = None
    description: str | None = Field(default=None, max_length=2000)
    color: str | None = Field(default=None, max_length=20)
    icon: str | None = Field(default=None, max_length=80)
    sort_order: int = 0
    is_active: bool = True


class RestaurantSectorResponse(RestaurantSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    floor_id: UUID | None
    code: str
    name: str
    description: str | None
    type: RestaurantSectorType
    color: str | None
    icon: str | None
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RestaurantStaffRequest(RestaurantSchema):
    code: str = Field(min_length=1, max_length=40)
    name: str = Field(min_length=1, max_length=160)
    role: RestaurantStaffRole = RestaurantStaffRole.WAITER
    status: RestaurantStaffStatus = RestaurantStaffStatus.AVAILABLE
    sector_id: UUID | None = None
    user_id: UUID | None = None
    can_receive_online_orders: bool = True
    is_active: bool = True


class RestaurantStaffResponse(RestaurantSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    user_id: UUID | None
    sector_id: UUID | None
    code: str
    name: str
    role: RestaurantStaffRole
    status: RestaurantStaffStatus
    can_receive_online_orders: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class RestaurantMenuAvailabilityRequest(RestaurantSchema):
    product_id: UUID
    service_date: date
    service_period: str = Field(default="all_day", min_length=1, max_length=40)
    channels: list[str] = Field(min_length=1, max_length=8)
    available_quantity: int | None = Field(default=None, ge=0)
    status: RestaurantMenuAvailabilityStatus = RestaurantMenuAvailabilityStatus.PUBLISHED
    is_active: bool = True


class RestaurantMenuAvailabilityResponse(RestaurantSchema):
    id: UUID
    tenant_id: UUID
    branch_id: UUID
    product_id: UUID
    service_date: date
    service_period: str
    channels: list[str]
    available_quantity: int | None
    sold_quantity: int
    status: RestaurantMenuAvailabilityStatus
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


class RestaurantTablePublicAccessResponse(RestaurantSchema):
    number: str
    name: str | None
    is_active: bool
