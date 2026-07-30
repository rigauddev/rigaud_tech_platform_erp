from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


class CompanyRepository(ABC):
    @abstractmethod
    async def add(self, company: CompanyModel) -> CompanyModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, company_id: UUID) -> CompanyModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_slug(self, slug: str) -> CompanyModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_code(self, code: str) -> CompanyModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_document(self, document: str) -> CompanyModel | None:
        raise NotImplementedError

    @abstractmethod
    async def resolve_by_slug_or_code(self, value: str) -> CompanyModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        limit: int,
        offset: int,
        status: CompanyStatus | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[CompanyModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        status: CompanyStatus | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_code(self, code: str, exclude_id: UUID | None = None) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_document(self, document: str, exclude_id: UUID | None = None) -> bool:
        raise NotImplementedError
