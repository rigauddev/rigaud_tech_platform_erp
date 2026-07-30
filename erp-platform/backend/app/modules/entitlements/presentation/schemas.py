from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EntitlementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tenant_id: UUID
    subscription_id: UUID | None
    entitlement_key: str
    entitlement_type: str
    is_enabled: bool
    source: str


class EntitlementCheckResponse(BaseModel):
    tenant_id: UUID
    entitlement_key: str
    is_enabled: bool
