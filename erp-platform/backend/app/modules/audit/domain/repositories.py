from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.audit.infrastructure.models import AuditEventModel


class AuditEventRepository(ABC):
    @abstractmethod
    async def add(self, event: AuditEventModel) -> AuditEventModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, event_id: UUID) -> AuditEventModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        limit: int,
        offset: int,
        tenant_id: UUID | None = None,
        actor_user_id: UUID | None = None,
        event_name: str | None = None,
        module: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[AuditEventModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID | None = None,
        actor_user_id: UUID | None = None,
        event_name: str | None = None,
        module: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        request_id: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> int:
        raise NotImplementedError
