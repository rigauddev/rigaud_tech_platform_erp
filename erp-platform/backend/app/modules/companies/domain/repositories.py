from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.companies.domain.entities import BranchStatus, CompanyStatus, MembershipStatus
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)


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


class BranchRepository(ABC):
    @abstractmethod
    async def add(self, branch: BranchModel) -> BranchModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, branch_id: UUID) -> BranchModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
        status: BranchStatus | None = None,
    ) -> list[BranchModel]:
        raise NotImplementedError

    @abstractmethod
    async def count_by_tenant(self, tenant_id: UUID, status: BranchStatus | None = None) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_code(
        self, tenant_id: UUID, code: str, exclude_id: UUID | None = None
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_document(
        self, tenant_id: UUID, document: str, exclude_id: UUID | None = None
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def has_headquarters(self, tenant_id: UUID, exclude_id: UUID | None = None) -> bool:
        raise NotImplementedError


class MembershipRepository(ABC):
    @abstractmethod
    async def add_company_membership(
        self, membership: CompanyMembershipModel
    ) -> CompanyMembershipModel:
        raise NotImplementedError

    @abstractmethod
    async def add_branch_membership(
        self, membership: BranchMembershipModel
    ) -> BranchMembershipModel:
        raise NotImplementedError

    @abstractmethod
    async def get_company_membership(
        self, user_id: UUID, tenant_id: UUID
    ) -> CompanyMembershipModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_default_company_membership(self, user_id: UUID) -> CompanyMembershipModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list_company_memberships(
        self, user_id: UUID, status: MembershipStatus | None = None
    ) -> list[CompanyMembershipModel]:
        raise NotImplementedError

    @abstractmethod
    async def get_branch_membership(
        self, company_membership_id: UUID, branch_id: UUID
    ) -> BranchMembershipModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_default_branch_membership(
        self, company_membership_id: UUID
    ) -> BranchMembershipModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list_branch_memberships(
        self,
        company_membership_id: UUID,
        status: MembershipStatus | None = None,
    ) -> list[BranchMembershipModel]:
        raise NotImplementedError
