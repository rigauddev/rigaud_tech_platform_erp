from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantTableRepository,
)
from app.modules.restaurant.infrastructure.models import RestaurantFloorModel, RestaurantTableModel


class SQLAlchemyRestaurantFloorRepository(RestaurantFloorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: RestaurantFloorModel) -> RestaurantFloorModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantFloorModel | None:
        result = await self.session.execute(
            select(RestaurantFloorModel).where(
                RestaurantFloorModel.id == item_id,
                RestaurantFloorModel.tenant_id == tenant_id,
                RestaurantFloorModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, is_active: bool | None
    ) -> list[RestaurantFloorModel]:
        statement = select(RestaurantFloorModel).where(
            RestaurantFloorModel.tenant_id == tenant_id,
            RestaurantFloorModel.branch_id == branch_id,
            RestaurantFloorModel.deleted_at.is_(None),
        )
        if is_active is not None:
            statement = statement.where(RestaurantFloorModel.is_active == is_active)
        result = await self.session.execute(
            statement.order_by(RestaurantFloorModel.sort_order, RestaurantFloorModel.name)
        )
        return list(result.scalars().all())

    async def exists_by_code(
        self, code: str, *, tenant_id: UUID, branch_id: UUID, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(RestaurantFloorModel.id).where(
            RestaurantFloorModel.tenant_id == tenant_id,
            RestaurantFloorModel.branch_id == branch_id,
            RestaurantFloorModel.code == code,
            RestaurantFloorModel.deleted_at.is_(None),
        )
        if exclude_id:
            statement = statement.where(RestaurantFloorModel.id != exclude_id)
        return (await self.session.execute(statement.limit(1))).scalar_one_or_none() is not None


class SQLAlchemyRestaurantTableRepository(RestaurantTableRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: RestaurantTableModel) -> RestaurantTableModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantTableModel | None:
        result = await self.session.execute(
            select(RestaurantTableModel).where(
                RestaurantTableModel.id == item_id,
                RestaurantTableModel.tenant_id == tenant_id,
                RestaurantTableModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, floor_id: UUID | None, is_active: bool | None
    ) -> list[RestaurantTableModel]:
        statement = select(RestaurantTableModel).where(
            RestaurantTableModel.tenant_id == tenant_id,
            RestaurantTableModel.branch_id == branch_id,
            RestaurantTableModel.deleted_at.is_(None),
        )
        if floor_id:
            statement = statement.where(RestaurantTableModel.floor_id == floor_id)
        if is_active is not None:
            statement = statement.where(RestaurantTableModel.is_active == is_active)
        result = await self.session.execute(
            statement.order_by(RestaurantTableModel.sort_order, RestaurantTableModel.number)
        )
        return list(result.scalars().all())

    async def exists_by_number(
        self, number: str, *, tenant_id: UUID, floor_id: UUID, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(RestaurantTableModel.id).where(
            RestaurantTableModel.tenant_id == tenant_id,
            RestaurantTableModel.floor_id == floor_id,
            RestaurantTableModel.number == number,
            RestaurantTableModel.deleted_at.is_(None),
        )
        if exclude_id:
            statement = statement.where(RestaurantTableModel.id != exclude_id)
        return (await self.session.execute(statement.limit(1))).scalar_one_or_none() is not None
