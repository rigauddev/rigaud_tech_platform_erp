from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.categories.application.validators import (
    normalize_color,
    normalize_display_order,
    normalize_icon,
    normalize_internal_code,
    normalize_optional_text,
    normalize_slug,
    normalize_text,
)
from app.modules.categories.domain.entities import CategoryStatus
from app.modules.categories.domain.exceptions import (
    CategoryAlreadyExistsError,
    CategoryCycleError,
    CategoryInternalCodeAlreadyExistsError,
    CategoryInUseError,
    CategoryNotFoundError,
    CategorySlugAlreadyExistsError,
)
from app.modules.categories.domain.repositories import CategoryRepository
from app.modules.categories.infrastructure.models import CategoryModel


@dataclass(frozen=True)
class CategoryCreateInput:
    tenant_id: UUID
    internal_code: str
    name: str
    parent_id: UUID | None = None
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int = 0
    actor_id: UUID | None = None


@dataclass(frozen=True)
class CategoryUpdateInput:
    internal_code: str | None = None
    name: str | None = None
    parent_id: UUID | None = None
    parent_id_provided: bool = False
    slug: str | None = None
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    display_order: int | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class CategoryListInput:
    tenant_id: UUID
    page: int = 1
    page_size: int = 20
    status: CategoryStatus | None = None
    parent_id: UUID | None = None
    search: str | None = None
    ordering: str = "manual"
    tree: bool = False


@dataclass(frozen=True)
class CategoryListResult:
    items: list[CategoryModel]
    total: int
    page: int
    page_size: int


class CreateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(self, input_data: CategoryCreateInput) -> CategoryModel:
        name = normalize_text(input_data.name, "name", max_length=120)
        internal_code = normalize_internal_code(input_data.internal_code)
        slug = normalize_slug(input_data.slug, fallback_name=name)
        await self._ensure_unique(
            tenant_id=input_data.tenant_id,
            internal_code=internal_code,
            slug=slug,
        )
        if input_data.parent_id is not None:
            await _ensure_parent_exists(
                self.categories,
                input_data.parent_id,
                tenant_id=input_data.tenant_id,
            )

        category = CategoryModel(
            tenant_id=input_data.tenant_id,
            parent_id=input_data.parent_id,
            internal_code=internal_code,
            name=name,
            slug=slug,
            description=normalize_optional_text(
                input_data.description,
                "description",
                max_length=500,
            ),
            icon=normalize_icon(input_data.icon),
            color=normalize_color(input_data.color),
            display_order=normalize_display_order(input_data.display_order),
            status=CategoryStatus.ACTIVE,
            is_active=True,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            return await self.categories.add(category)
        except IntegrityError as exc:
            raise CategoryAlreadyExistsError("Category already exists.") from exc

    async def _ensure_unique(self, *, tenant_id: UUID, internal_code: str, slug: str) -> None:
        if await self.categories.exists_by_internal_code(internal_code, tenant_id=tenant_id):
            raise CategoryInternalCodeAlreadyExistsError("Internal code already exists.")
        if await self.categories.exists_by_slug(slug, tenant_id=tenant_id):
            raise CategorySlugAlreadyExistsError("Slug already exists.")


class GetCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(self, category_id: UUID, *, tenant_id: UUID) -> CategoryModel:
        category = await self.categories.get_by_id(category_id, tenant_id=tenant_id)
        if category is None:
            raise CategoryNotFoundError("Category not found.")
        return category


class ListCategories:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(self, input_data: CategoryListInput) -> CategoryListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        limit = None if input_data.tree else page_size
        items = await self.categories.list(
            tenant_id=input_data.tenant_id,
            limit=limit,
            offset=0 if input_data.tree else offset,
            status=input_data.status,
            parent_id=input_data.parent_id,
            search=search,
            ordering=input_data.ordering,
        )
        total = await self.categories.count(
            tenant_id=input_data.tenant_id,
            status=input_data.status,
            parent_id=input_data.parent_id,
            search=search,
        )
        return CategoryListResult(items=items, total=total, page=page, page_size=page_size)


class UpdateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(
        self,
        category_id: UUID,
        *,
        tenant_id: UUID,
        input_data: CategoryUpdateInput,
    ) -> CategoryModel:
        category = await GetCategory(self.categories).execute(category_id, tenant_id=tenant_id)

        if input_data.parent_id_provided:
            if input_data.parent_id is None:
                category.parent_id = None
            else:
                await _ensure_parent_exists(
                    self.categories,
                    input_data.parent_id,
                    tenant_id=tenant_id,
                )
                await _ensure_no_cycle(
                    self.categories,
                    category_id=category.id,
                    parent_id=input_data.parent_id,
                    tenant_id=tenant_id,
                )
                category.parent_id = input_data.parent_id
        if input_data.name is not None:
            category.name = normalize_text(input_data.name, "name", max_length=120)
        if input_data.internal_code is not None:
            internal_code = normalize_internal_code(input_data.internal_code)
            if await self.categories.exists_by_internal_code(
                internal_code,
                tenant_id=tenant_id,
                exclude_id=category.id,
            ):
                raise CategoryInternalCodeAlreadyExistsError("Internal code already exists.")
            category.internal_code = internal_code
        if input_data.slug is not None:
            slug = normalize_slug(input_data.slug, fallback_name=category.name)
            if await self.categories.exists_by_slug(
                slug, tenant_id=tenant_id, exclude_id=category.id
            ):
                raise CategorySlugAlreadyExistsError("Slug already exists.")
            category.slug = slug
        if input_data.description is not None:
            category.description = normalize_optional_text(
                input_data.description,
                "description",
                max_length=500,
            )
        if input_data.icon is not None:
            category.icon = normalize_icon(input_data.icon)
        if input_data.color is not None:
            category.color = normalize_color(input_data.color)
        if input_data.display_order is not None:
            category.display_order = normalize_display_order(input_data.display_order)
        category.updated_by = input_data.actor_id
        try:
            return await self.categories.add(category)
        except IntegrityError as exc:
            raise CategoryAlreadyExistsError("Category already exists.") from exc


class ActivateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(
        self,
        category_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> CategoryModel:
        category = await GetCategory(self.categories).execute(category_id, tenant_id=tenant_id)
        category.activate()
        category.updated_by = actor_id
        return await self.categories.add(category)


class DeactivateCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(
        self,
        category_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> CategoryModel:
        category = await GetCategory(self.categories).execute(category_id, tenant_id=tenant_id)
        category.deactivate()
        category.updated_by = actor_id
        return await self.categories.add(category)


class ReorderCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(
        self,
        category_id: UUID,
        *,
        tenant_id: UUID,
        display_order: int,
        actor_id: UUID | None = None,
    ) -> CategoryModel:
        category = await GetCategory(self.categories).execute(category_id, tenant_id=tenant_id)
        category.display_order = normalize_display_order(display_order)
        category.updated_by = actor_id
        return await self.categories.add(category)


class DeleteCategory:
    def __init__(self, categories: CategoryRepository) -> None:
        self.categories = categories

    async def execute(
        self,
        category_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> CategoryModel:
        category = await GetCategory(self.categories).execute(category_id, tenant_id=tenant_id)
        if await self.categories.has_children(category.id, tenant_id=tenant_id):
            raise CategoryInUseError("Category has child categories.")
        category.deactivate()
        category.mark_as_deleted()
        category.deleted_by = actor_id
        category.updated_by = actor_id
        return await self.categories.add(category)


async def _ensure_parent_exists(
    categories: CategoryRepository,
    parent_id: UUID,
    *,
    tenant_id: UUID,
) -> CategoryModel:
    parent = await categories.get_by_id(parent_id, tenant_id=tenant_id)
    if parent is None:
        raise CategoryNotFoundError("Parent category not found.")
    return parent


async def _ensure_no_cycle(
    categories: CategoryRepository,
    *,
    category_id: UUID,
    parent_id: UUID,
    tenant_id: UUID,
) -> None:
    if parent_id == category_id:
        raise CategoryCycleError("Category cannot be its own parent.")
    current_parent_id: UUID | None = parent_id
    visited: set[UUID] = set()
    while current_parent_id is not None:
        if current_parent_id in visited or current_parent_id == category_id:
            raise CategoryCycleError("Category hierarchy cycle detected.")
        visited.add(current_parent_id)
        parent = await categories.get_by_id(current_parent_id, tenant_id=tenant_id)
        if parent is None:
            raise CategoryNotFoundError("Parent category not found.")
        current_parent_id = parent.parent_id
