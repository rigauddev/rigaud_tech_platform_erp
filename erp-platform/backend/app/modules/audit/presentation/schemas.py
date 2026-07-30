from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AuditEventResponse(AuditSchema):
    id: UUID
    event_name: str
    module: str
    action: str
    entity_type: str | None
    entity_id: str | None
    tenant_id: UUID | None
    actor_user_id: UUID | None
    request_id: str | None
    correlation_id: str | None
    source: str
    ip_address: str | None
    user_agent: str | None
    before_data: dict | None
    after_data: dict | None
    metadata: dict | None
    occurred_at: datetime
    created_at: datetime
