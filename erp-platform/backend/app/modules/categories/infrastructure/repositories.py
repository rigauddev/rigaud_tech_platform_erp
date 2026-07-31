from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.categories.domain.entities import CategoryStatus
from app.modules.categories.domain.repositories import CategoryRepository
from app.modules.categories.infrastructure.models import CategoryModel


class SQLAlchemyCategoryRepository(CategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, category: CategoryModel) -> CategoryModel:
        self.session.add(category)
        await self.session.flush()
        return category

    async def get_by_id(self, category_id: UUID, *, tenant_id: UUID) -> CategoryModel | None:
        result = await self.session.execute(
            select(CategoryModel).where(
                CategoryModel.id == category_id,
                CategoryModel.tenant_id == tenant_id,
                CategoryModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        tenant_id: UUID,
        limit: int | None = None,
        offset: int = 0,
        status: CategoryStatus | None = None,
        parent_id: UUID | None = None,
        search: str | None = None,
        ordering: str = "manual",
    ) -> list[CategoryModel]:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            status=status,
            parent_id=parent_id,
            search=search,
        )
        if ordering == "name":
            statement = statement.order_by(CategoryModel.name)
        else:
            statement = statement.order_by(CategoryModel.display_order, CategoryModel.name)
        if limit is not None:
            statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        tenant_id: UUID,
        status: CategoryStatus | None = None,
        parent_id: UUID | None = None,
        search: str | None = None,
    ) -> int:
        statement = self._filtered_select(
            tenant_id=tenant_id,
            status=status,
            parent_id=parent_id,
            search=search,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_internal_code(
        self,
        internal_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return await self._exists(
            CategoryModel.internal_code == internal_code,
            tenant_id=tenant_id,
            exclude_id=exclude_id,
        )

    async def exists_by_slug(
        self,
        slug: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return await self._exists(
            CategoryModel.slug == slug,
            tenant_id=tenant_id,
            exclude_id=exclude_id,
        )

    async def has_children(self, category_id: UUID, *, tenant_id: UUID) -> bool:
        result = await self.session.execute(
            select(CategoryModel.id)
            .where(
                CategoryModel.tenant_id == tenant_id,
                CategoryModel.parent_id == category_id,
                CategoryModel.deleted_at.is_(None),
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    def _filtered_select(
        self,
        *,
        tenant_id: UUID,
        status: CategoryStatus | None,
        parent_id: UUID | None,
        search: str | None,
    ) -> Select[tuple[CategoryModel]]:
        statement = select(CategoryModel).where(
            CategoryModel.tenant_id == tenant_id,
            CategoryModel.deleted_at.is_(None),
        )
        if status is not None:
            statement = statement.where(CategoryModel.status == status)
        if parent_id is not None:
            statement = statement.where(CategoryModel.parent_id == parent_id)
        if search:
            like = f"%{search.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(CategoryModel.name).like(like),
                    func.lower(CategoryModel.internal_code).like(like),
                    func.lower(CategoryModel.slug).like(like),
                )
            )
        return statement

    async def _exists(
        self,
        condition,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(CategoryModel.id).where(
            condition,
            CategoryModel.tenant_id == tenant_id,
            CategoryModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(CategoryModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None
