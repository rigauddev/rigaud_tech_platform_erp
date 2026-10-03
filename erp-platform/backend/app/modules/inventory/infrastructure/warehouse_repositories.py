from uuid import UUID

from sqlalchemy import Select, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import WarehouseModel


class SQLAlchemyWarehouseRepository(WarehouseRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, warehouse: WarehouseModel) -> WarehouseModel:
        self.session.add(warehouse)
        await self.session.flush()
        return warehouse

    async def get_by_id(self, warehouse_id: UUID, *, tenant_id: UUID) -> WarehouseModel | None:
        result = await self.session.execute(
            select(WarehouseModel).where(
                WarehouseModel.id == warehouse_id,
                WarehouseModel.tenant_id == tenant_id,
                WarehouseModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseModel]:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            is_active=is_active,
        )
        statement = (
            statement.order_by(
                WarehouseModel.is_default.desc(),
                WarehouseModel.name,
            )
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            is_active=is_active,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(WarehouseModel.id).where(
            WarehouseModel.tenant_id == tenant_id,
            WarehouseModel.branch_id == branch_id,
            WarehouseModel.code == code,
            WarehouseModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(WarehouseModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    async def unset_default_for_branch(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        except_id: UUID | None = None,
    ) -> None:
        statement = update(WarehouseModel).where(
            WarehouseModel.tenant_id == tenant_id,
            WarehouseModel.branch_id == branch_id,
            WarehouseModel.deleted_at.is_(None),
        )
        if except_id is not None:
            statement = statement.where(WarehouseModel.id != except_id)
        await self.session.execute(statement.values(is_default=False))

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> Select[tuple[WarehouseModel]]:
        statement = select(WarehouseModel).where(
            WarehouseModel.tenant_id == tenant_id,
            WarehouseModel.deleted_at.is_(None),
        )
        if branch_id is not None:
            statement = statement.where(WarehouseModel.branch_id == branch_id)
        if is_active is not None:
            statement = statement.where(WarehouseModel.is_active == is_active)
        return statement
