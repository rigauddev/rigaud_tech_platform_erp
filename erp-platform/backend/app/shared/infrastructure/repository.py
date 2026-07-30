from typing import TypeVar
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

EntityT = TypeVar("EntityT")


class SQLAlchemyAsyncRepository[EntityT]:
    """Infraestrutura base para repositories SQLAlchemy futuros."""

    def __init__(self, session: AsyncSession, model: type[EntityT]) -> None:
        self.session = session
        self.model = model

    async def get_by_id(self, entity_id: UUID) -> EntityT | None:
        return await self.session.get(self.model, entity_id)

    async def add(self, entity: EntityT) -> EntityT:
        self.session.add(entity)
        return entity

    async def delete(self, entity: EntityT) -> None:
        await self.session.delete(entity)

    async def flush(self) -> None:
        await self.session.flush()

    async def refresh(self, entity: EntityT) -> None:
        await self.session.refresh(entity)
