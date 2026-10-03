from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.domain.warehouse_location_repositories import (
    WarehouseLocationRepository,
)
from app.modules.inventory.infrastructure.models import WarehouseLocationModel


class SQLAlchemyWarehouseLocationRepository(WarehouseLocationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, location: WarehouseLocationModel) -> WarehouseLocationModel:
        self.session.add(location)
        await self.session.flush()
        return location

    async def get_by_id(
        self, location_id: UUID, *, tenant_id: UUID
    ) -> WarehouseLocationModel | None:
        result = await self.session.execute(
            select(WarehouseLocationModel).where(
                WarehouseLocationModel.id == location_id,
                WarehouseLocationModel.tenant_id == tenant_id,
                WarehouseLocationModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseLocationModel]:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            zone_id=zone_id,
            search=search,
            is_active=is_active,
        )
        statement = (
            statement.order_by(WarehouseLocationModel.sort_order, WarehouseLocationModel.code)
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
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
    ) -> int:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse_id,
            zone_id=zone_id,
            search=search,
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
        statement = select(WarehouseLocationModel.id).where(
            WarehouseLocationModel.tenant_id == tenant_id,
            WarehouseLocationModel.warehouse_id == warehouse_id,
            WarehouseLocationModel.code == code,
            WarehouseLocationModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(WarehouseLocationModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(WarehouseLocationModel.id).where(
            WarehouseLocationModel.tenant_id == tenant_id,
            WarehouseLocationModel.barcode == barcode,
            WarehouseLocationModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(WarehouseLocationModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    async def exists_by_qr_code(
        self,
        qr_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(WarehouseLocationModel.id).where(
            WarehouseLocationModel.tenant_id == tenant_id,
            WarehouseLocationModel.qr_code == qr_code,
            WarehouseLocationModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(WarehouseLocationModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
    ) -> Select[tuple[WarehouseLocationModel]]:
        statement = select(WarehouseLocationModel).where(
            WarehouseLocationModel.tenant_id == tenant_id,
            WarehouseLocationModel.deleted_at.is_(None),
        )
        if branch_id is not None:
            statement = statement.where(WarehouseLocationModel.branch_id == branch_id)
        if warehouse_id is not None:
            statement = statement.where(WarehouseLocationModel.warehouse_id == warehouse_id)
        if zone_id is not None:
            statement = statement.where(WarehouseLocationModel.zone_id == zone_id)
        if is_active is not None:
            statement = statement.where(WarehouseLocationModel.is_active == is_active)
        if search:
            term = f"%{search.strip()}%"
            statement = statement.where(
                or_(
                    WarehouseLocationModel.code.ilike(term),
                    WarehouseLocationModel.name.ilike(term),
                    WarehouseLocationModel.alias.ilike(term),
                    WarehouseLocationModel.barcode.ilike(term),
                    WarehouseLocationModel.qr_code.ilike(term),
                )
            )
        return statement
