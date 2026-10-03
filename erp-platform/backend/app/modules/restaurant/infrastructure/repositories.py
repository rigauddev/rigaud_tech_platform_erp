from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.products.infrastructure.models import ProductModel
from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantMenuAvailabilityRepository,
    RestaurantSectorRepository,
    RestaurantStaffRepository,
    RestaurantTableRepository,
)
from app.modules.restaurant.infrastructure.models import (
    RestaurantFloorModel,
    RestaurantMenuAvailabilityModel,
    RestaurantSectorModel,
    RestaurantStaffModel,
    RestaurantTableModel,
)


class SQLAlchemyRestaurantMenuAvailabilityRepository(RestaurantMenuAvailabilityRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: RestaurantMenuAvailabilityModel) -> RestaurantMenuAvailabilityModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(
        self, item_id: UUID, *, tenant_id: UUID
    ) -> RestaurantMenuAvailabilityModel | None:
        result = await self.session.execute(
            select(RestaurantMenuAvailabilityModel).where(
                RestaurantMenuAvailabilityModel.id == item_id,
                RestaurantMenuAvailabilityModel.tenant_id == tenant_id,
                RestaurantMenuAvailabilityModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        service_date: object | None,
        service_period: str | None,
    ) -> list[RestaurantMenuAvailabilityModel]:
        statement = select(RestaurantMenuAvailabilityModel).where(
            RestaurantMenuAvailabilityModel.tenant_id == tenant_id,
            RestaurantMenuAvailabilityModel.branch_id == branch_id,
            RestaurantMenuAvailabilityModel.deleted_at.is_(None),
        )
        if service_date is not None:
            statement = statement.where(
                RestaurantMenuAvailabilityModel.service_date == service_date
            )
        if service_period:
            statement = statement.where(
                RestaurantMenuAvailabilityModel.service_period == service_period
            )
        result = await self.session.execute(
            statement.order_by(
                RestaurantMenuAvailabilityModel.service_date.desc(),
                RestaurantMenuAvailabilityModel.service_period,
            )
        )
        return list(result.scalars().all())

    async def exists_in_scope(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        service_date: object,
        service_period: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(RestaurantMenuAvailabilityModel.id).where(
            RestaurantMenuAvailabilityModel.tenant_id == tenant_id,
            RestaurantMenuAvailabilityModel.branch_id == branch_id,
            RestaurantMenuAvailabilityModel.product_id == product_id,
            RestaurantMenuAvailabilityModel.service_date == service_date,
            RestaurantMenuAvailabilityModel.service_period == service_period,
            RestaurantMenuAvailabilityModel.deleted_at.is_(None),
        )
        if exclude_id:
            statement = statement.where(RestaurantMenuAvailabilityModel.id != exclude_id)
        return (await self.session.execute(statement.limit(1))).scalar_one_or_none() is not None

    async def product_exists(self, product_id: UUID, *, tenant_id: UUID) -> bool:
        return (
            await self.session.execute(
                select(ProductModel.id)
                .where(
                    ProductModel.id == product_id,
                    ProductModel.tenant_id == tenant_id,
                    ProductModel.deleted_at.is_(None),
                )
                .limit(1)
            )
        ).scalar_one_or_none() is not None


class SQLAlchemyRestaurantStaffRepository(RestaurantStaffRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: RestaurantStaffModel) -> RestaurantStaffModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantStaffModel | None:
        result = await self.session.execute(
            select(RestaurantStaffModel).where(
                RestaurantStaffModel.id == item_id,
                RestaurantStaffModel.tenant_id == tenant_id,
                RestaurantStaffModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, search: str | None = None
    ) -> list[RestaurantStaffModel]:
        statement = select(RestaurantStaffModel).where(
            RestaurantStaffModel.tenant_id == tenant_id,
            RestaurantStaffModel.branch_id == branch_id,
            RestaurantStaffModel.deleted_at.is_(None),
        )
        if search:
            statement = statement.where(RestaurantStaffModel.name.ilike(f"%{search.strip()}%"))
        result = await self.session.execute(statement.order_by(RestaurantStaffModel.name))
        return list(result.scalars().all())

    async def exists_by_code(
        self, code: str, *, tenant_id: UUID, branch_id: UUID, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(RestaurantStaffModel.id).where(
            RestaurantStaffModel.tenant_id == tenant_id,
            RestaurantStaffModel.branch_id == branch_id,
            RestaurantStaffModel.code == code,
            RestaurantStaffModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(RestaurantStaffModel.id != exclude_id)
        return (await self.session.execute(statement.limit(1))).scalar_one_or_none() is not None


class SQLAlchemyRestaurantSectorRepository(RestaurantSectorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, item: RestaurantSectorModel) -> RestaurantSectorModel:
        self.session.add(item)
        await self.session.flush()
        return item

    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantSectorModel | None:
        result = await self.session.execute(
            select(RestaurantSectorModel).where(
                RestaurantSectorModel.id == item_id,
                RestaurantSectorModel.tenant_id == tenant_id,
                RestaurantSectorModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, is_active: bool | None
    ) -> list[RestaurantSectorModel]:
        statement = select(RestaurantSectorModel).where(
            RestaurantSectorModel.tenant_id == tenant_id,
            RestaurantSectorModel.branch_id == branch_id,
            RestaurantSectorModel.deleted_at.is_(None),
        )
        if is_active is not None:
            statement = statement.where(RestaurantSectorModel.is_active == is_active)
        result = await self.session.execute(
            statement.order_by(RestaurantSectorModel.sort_order, RestaurantSectorModel.name)
        )
        return list(result.scalars().all())

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(RestaurantSectorModel.id).where(
            RestaurantSectorModel.tenant_id == tenant_id,
            RestaurantSectorModel.branch_id == branch_id,
            RestaurantSectorModel.code == code,
            RestaurantSectorModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(RestaurantSectorModel.id != exclude_id)
        return (await self.session.execute(statement.limit(1))).scalar_one_or_none() is not None


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
