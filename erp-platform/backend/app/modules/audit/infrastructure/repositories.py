from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.domain.repositories import AuditEventRepository
from app.modules.audit.infrastructure.models import AuditEventModel


class SQLAlchemyAuditEventRepository(AuditEventRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, event: AuditEventModel) -> AuditEventModel:
        self.session.add(event)
        await self.session.flush()
        return event

    async def get_by_id(self, event_id: UUID) -> AuditEventModel | None:
        return await self.session.get(AuditEventModel, event_id)

    async def list(self, *, limit: int, offset: int, **filters) -> list[AuditEventModel]:
        statement = self._filtered_select(**filters)
        statement = (
            statement.order_by(AuditEventModel.occurred_at.desc()).limit(limit).offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(self, **filters) -> int:
        statement = self._filtered_select(**filters)
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    def _filtered_select(
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
    ) -> Select[tuple[AuditEventModel]]:
        statement = select(AuditEventModel)
        if tenant_id is not None:
            statement = statement.where(AuditEventModel.tenant_id == tenant_id)
        if actor_user_id is not None:
            statement = statement.where(AuditEventModel.actor_user_id == actor_user_id)
        if event_name:
            statement = statement.where(AuditEventModel.event_name == event_name)
        if module:
            statement = statement.where(AuditEventModel.module == module)
        if entity_type:
            statement = statement.where(AuditEventModel.entity_type == entity_type)
        if entity_id:
            statement = statement.where(AuditEventModel.entity_id == entity_id)
        if request_id:
            statement = statement.where(AuditEventModel.request_id == request_id)
        if date_from:
            statement = statement.where(AuditEventModel.occurred_at >= date_from)
        if date_to:
            statement = statement.where(AuditEventModel.occurred_at <= date_to)
        return statement
