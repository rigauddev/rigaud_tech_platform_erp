from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.categories.domain.entities import CategoryStatus
from app.modules.categories.infrastructure.models import CategoryModel


class CategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: CategoryModel) -> CategoryModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, category_id: UUID, *, tenant_id: UUID) -> CategoryModel | None:
        raise NotImplementedError

    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        status: CategoryStatus | None = None,
        parent_id: UUID | None = None,
        search: str | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_internal_code(
        self,
        internal_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_slug(
        self,
        slug: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def has_children(self, category_id: UUID, *, tenant_id: UUID) -> bool:
        raise NotImplementedError
