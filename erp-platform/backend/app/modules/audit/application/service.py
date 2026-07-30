from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.modules.audit.domain.repositories import AuditEventRepository
from app.modules.audit.infrastructure.models import AuditEventModel
from app.shared.observability.context import get_correlation_id, get_request_id
from app.shared.observability.sanitizer import sanitize_mapping, sanitize_value


@dataclass(frozen=True)
class AuditEventInput:
    event_name: str
    module: str
    action: str
    entity_type: str | None = None
    entity_id: str | UUID | None = None
    tenant_id: UUID | None = None
    actor_user_id: UUID | None = None
    source: str = "api"
    ip_address: str | None = None
    user_agent: str | None = None
    before_data: dict[str, Any] | None = None
    after_data: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None
    reason: str | None = None


class AuditService:
    def __init__(self, repository: AuditEventRepository) -> None:
        self.repository = repository

    async def record_event(self, input_data: AuditEventInput) -> AuditEventModel:
        event = AuditEventModel(
            event_name=input_data.event_name,
            module=input_data.module,
            action=input_data.action,
            entity_type=input_data.entity_type,
            entity_id=str(input_data.entity_id) if input_data.entity_id is not None else None,
            tenant_id=input_data.tenant_id,
            actor_user_id=input_data.actor_user_id,
            request_id=get_request_id(),
            correlation_id=get_correlation_id(),
            source=input_data.source,
            ip_address=sanitize_value("ip_address", input_data.ip_address),
            user_agent=sanitize_value("user_agent", input_data.user_agent),
            before_data=sanitize_mapping(input_data.before_data),
            after_data=sanitize_mapping(input_data.after_data),
            event_metadata=sanitize_mapping(input_data.metadata),
            reason=input_data.reason,
            occurred_at=datetime.now(UTC),
        )
        return await self.repository.add(event)
