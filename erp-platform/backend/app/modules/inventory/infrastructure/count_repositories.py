from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.inventory.domain.entities import InventoryCountStatus
from app.modules.inventory.infrastructure.models import InventoryCountModel


class SQLAlchemyInventoryCountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, count: InventoryCountModel) -> InventoryCountModel:
        self.session.add(count)
        await self.session.flush()
        await self.session.refresh(count, attribute_names=["items"])
        return count

    async def get_by_id(self, count_id: UUID, *, tenant_id: UUID) -> InventoryCountModel | None:
        result = await self.session.execute(
            select(InventoryCountModel).options(selectinload(InventoryCountModel.items)).where(
                InventoryCountModel.id == count_id,
                InventoryCountModel.tenant_id == tenant_id,
                InventoryCountModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(self, *, tenant_id: UUID, branch_id: UUID | None, status: InventoryCountStatus | None, limit: int, offset: int) -> list[InventoryCountModel]:
        statement = self._select(tenant_id=tenant_id, branch_id=branch_id, status=status).options(selectinload(InventoryCountModel.items)).order_by(InventoryCountModel.created_at.desc()).limit(limit).offset(offset)
        return list((await self.session.execute(statement)).scalars().all())

    async def count(self, *, tenant_id: UUID, branch_id: UUID | None, status: InventoryCountStatus | None) -> int:
        statement = self._select(tenant_id=tenant_id, branch_id=branch_id, status=status)
        return int((await self.session.execute(select(func.count()).select_from(statement.subquery()))).scalar_one())

    def _select(self, *, tenant_id: UUID, branch_id: UUID | None, status: InventoryCountStatus | None):
        statement = select(InventoryCountModel).where(InventoryCountModel.tenant_id == tenant_id, InventoryCountModel.deleted_at.is_(None))
        if branch_id is not None:
            statement = statement.where(InventoryCountModel.branch_id == branch_id)
        if status is not None:
            statement = statement.where(InventoryCountModel.status == status)
        return statement
