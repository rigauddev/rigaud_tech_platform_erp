from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.billing.domain.entities import BillingEventType


class BillingEventRequest(BaseModel):
    tenant_id: UUID
    subscription_id: UUID | None = None
    event_type: BillingEventType
    external_event_id: str | None = Field(default=None, max_length=120)
    payload: dict | None = None


class BillingEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    subscription_id: UUID | None
    provider: str
    event_type: str
    status: str
    external_event_id: str | None
    payload: dict | None
