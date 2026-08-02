from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.domain.warehouse_zone_repositories import WarehouseZoneRepository
from app.modules.inventory.infrastructure.models import WarehouseZoneModel


class SQLAlchemyWarehouseZoneRepository(WarehouseZoneRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, zone: WarehouseZoneModel) -> WarehouseZoneModel:
        self.session.add(zone)
        await self.session.flush()
        return zone

    async def get_by_id(self, zone_id: UUID, *, tenant_id: UUID) -> WarehouseZoneModel | None:
        result = await self.session.execute(
            select(WarehouseZoneModel).where(
                WarehouseZoneModel.id == zone_id,
                WarehouseZoneModel.tenant_id == tenant_id,
                WarehouseZoneModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseZoneModel]:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            is_active=is_active,
        )
        statement = (
            statement.order_by(
                WarehouseZoneModel.sort_order,
                WarehouseZoneModel.name,
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
        warehouse_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            is_active=is_active,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        warehouse_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(WarehouseZoneModel.id).where(
            WarehouseZoneModel.tenant_id == tenant_id,
            WarehouseZoneModel.warehouse_id == warehouse_id,
            WarehouseZoneModel.code == code,
            WarehouseZoneModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(WarehouseZoneModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
    ) -> Select[tuple[WarehouseZoneModel]]:
        statement = select(WarehouseZoneModel).where(
            WarehouseZoneModel.tenant_id == tenant_id,
            WarehouseZoneModel.deleted_at.is_(None),
        )
        if branch_id is not None:
            statement = statement.where(WarehouseZoneModel.branch_id == branch_id)
        if warehouse_id is not None:
            statement = statement.where(WarehouseZoneModel.warehouse_id == warehouse_id)
        if is_active is not None:
            statement = statement.where(WarehouseZoneModel.is_active == is_active)
        return statement
