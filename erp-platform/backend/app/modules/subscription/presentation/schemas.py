from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.subscription.domain.entities import SubscriptionStatus


class SubscriptionCreateRequest(BaseModel):
    tenant_id: UUID
    plan_id: UUID
    status: SubscriptionStatus = SubscriptionStatus.TRIAL
    billing_provider: str = Field(default="fake", max_length=40)
    grace_period_days: int = Field(default=7, ge=0)


class SubscriptionChangePlanRequest(BaseModel):
    plan_id: UUID


class SubscriptionStatusRequest(BaseModel):
    status: SubscriptionStatus


class SubscriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    plan_id: UUID
    status: str
    billing_provider: str
    external_reference: str | None
    started_at: datetime | None
    trial_ends_at: datetime | None
    current_period_starts_at: datetime | None
    current_period_ends_at: datetime | None
    grace_period_ends_at: datetime | None
    cancelled_at: datetime | None
    grace_period_days: int
