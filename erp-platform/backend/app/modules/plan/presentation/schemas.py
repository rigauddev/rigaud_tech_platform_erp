from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanEntitlementRequest(BaseModel):
    entitlement_key: str = Field(min_length=2, max_length=80)
    entitlement_type: str = Field(min_length=2, max_length=20)
    is_enabled: bool = True


class PlanLimitRequest(BaseModel):
    limit_key: str = Field(min_length=2, max_length=80)
    limit_value: int = Field(ge=0)
    is_unlimited: bool = False


class PlanCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=2, max_length=120)
    description: str | None = Field(default=None, max_length=500)
    monthly_price: Decimal = Field(ge=0)
    annual_price: Decimal = Field(ge=0)
    trial_days: int = Field(default=0, ge=0)
    is_trial_available: bool = False
    is_active: bool = True
    display_order: int = Field(default=0, ge=0)
    entitlements: list[PlanEntitlementRequest] = Field(default_factory=list)
    limits: list[PlanLimitRequest] = Field(default_factory=list)


class PlanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    monthly_price: Decimal
    annual_price: Decimal
    trial_days: int
    is_trial_available: bool
    is_active: bool
    display_order: int
    status: str
