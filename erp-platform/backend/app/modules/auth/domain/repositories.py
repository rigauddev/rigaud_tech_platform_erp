from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any
from uuid import UUID

from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.domain.mfa import MfaMethodType


class UserAuthRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_email_and_tenant_id(self, email: str, tenant_id: UUID) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def update_last_login(self, user: Any, logged_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def increment_failed_login(self, user: Any) -> None:
        raise NotImplementedError


class AuthSessionRepository(ABC):
    @abstractmethod
    async def create(self, session: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def get_by_refresh_token_hash(self, refresh_token_hash: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def revoke(self, session: Any, revoked_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_session_chain(self, session: Any, revoked_at: datetime) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        raise NotImplementedError


class TenantResolver(ABC):
    @abstractmethod
    async def resolve_by_slug_or_code(self, tenant: str) -> UUID | None:
        raise NotImplementedError

    @abstractmethod
    async def ensure_active(self, tenant_id: UUID) -> None:
        raise NotImplementedError


class MfaMethodRepository(ABC):
    @abstractmethod
    async def get_by_user_and_type(self, user_id: UUID, method_type: MfaMethodType) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id_for_user(
        self, method_id: UUID, user_id: UUID, tenant_id: UUID
    ) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def list_for_user(self, user_id: UUID, tenant_id: UUID) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def list_active_for_user(self, user_id: UUID, tenant_id: UUID) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def save(self, method: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def unset_primary_for_user(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    async def disable_all_for_user(self, user_id: UUID, disabled_at: datetime) -> None:
        raise NotImplementedError


class MfaRecoveryCodeRepository(ABC):
    @abstractmethod
    async def create_many(self, codes: list[Any]) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def list_active_for_user(self, user_id: UUID, tenant_id: UUID) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def get_active_by_hash(
        self, user_id: UUID, tenant_id: UUID, code_hash: str
    ) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def invalidate_all_for_user(self, user_id: UUID, used_at: datetime) -> None:
        raise NotImplementedError


class MfaChallengeStore(ABC):
    @abstractmethod
    async def create(self, payload: dict[str, Any], expires_in: int) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get(self, challenge_id: str) -> dict[str, Any] | None:
        raise NotImplementedError

    @abstractmethod
    async def update(self, challenge_id: str, payload: dict[str, Any], expires_in: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, challenge_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def revoke_user_challenges(self, user_id: UUID) -> None:
        raise NotImplementedError


class EmailOtpSender(ABC):
    @abstractmethod
    async def send_code(self, email: str, code: str) -> None:
        raise NotImplementedError


class SmsOtpSender(ABC):
    @abstractmethod
    async def send_code(self, phone: str, code: str) -> None:
        raise NotImplementedError


def to_authenticated_user(
    user: Any,
    *,
    tenant_id: UUID | None = None,
    membership_id: UUID | None = None,
    branch_id: UUID | None = None,
    branch_membership_id: UUID | None = None,
    role: str | None = None,
    access_scope: str | None = None,
) -> AuthenticatedUser:
    return AuthenticatedUser(
        id=user.id,
        tenant_id=tenant_id or user.tenant_id,
        tenant_slug=user.tenant_slug,
        email=user.email,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        deleted_at=user.deleted_at,
        membership_id=membership_id,
        branch_id=branch_id,
        branch_membership_id=branch_membership_id,
        role=role,
        access_scope=access_scope,
    )
