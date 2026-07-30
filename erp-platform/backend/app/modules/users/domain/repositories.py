from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.auth.infrastructure.models import AuthUserModel
from app.modules.users.domain.entities import UserStatus


class UserRepository(ABC):
    @abstractmethod
    async def add(self, user: AuthUserModel) -> AuthUserModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> AuthUserModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email_and_tenant_id(self, email: str, tenant_id: UUID) -> AuthUserModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        limit: int,
        offset: int,
        tenant_id: UUID | None = None,
        status: UserStatus | None = None,
        search: str | None = None,
    ) -> list[AuthUserModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID | None = None,
        status: UserStatus | None = None,
        search: str | None = None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_email_and_tenant_id(
        self,
        email: str,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError
