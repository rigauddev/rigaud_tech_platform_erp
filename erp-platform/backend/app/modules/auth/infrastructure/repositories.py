from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.domain.exceptions import TenantInactiveError, TenantSuspendedError
from app.modules.auth.domain.mfa import MfaMethodStatus, MfaMethodType
from app.modules.auth.domain.repositories import (
    AuthSessionRepository,
    MfaMethodRepository,
    MfaRecoveryCodeRepository,
    TenantResolver,
    UserAuthRepository,
)
from app.modules.auth.infrastructure.models import (
    AuthSessionModel,
    AuthUserModel,
    MfaRecoveryCodeModel,
    UserMfaMethodModel,
)
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


class SQLAlchemyUserAuthRepository(UserAuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email_and_tenant_id(self, email: str, tenant_id: UUID) -> AuthUserModel | None:
        result = await self.session.execute(
            select(AuthUserModel).where(
                AuthUserModel.email == email,
                AuthUserModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> AuthUserModel | None:
        return await self.session.get(AuthUserModel, user_id)

    async def update_last_login(self, user: AuthUserModel, logged_at: datetime) -> None:
        user.last_login_at = logged_at
        user.failed_login_attempts = 0
        user.locked_until = None
        await self.session.flush()

    async def increment_failed_login(self, user: AuthUserModel) -> None:
        user.failed_login_attempts += 1
        await self.session.flush()


class SQLAlchemyAuthSessionRepository(AuthSessionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, session: AuthSessionModel) -> AuthSessionModel:
        self.session.add(session)
        await self.session.flush()
        return session

    async def get_by_refresh_token_hash(self, refresh_token_hash: str) -> AuthSessionModel | None:
        result = await self.session.execute(
            select(AuthSessionModel).where(
                AuthSessionModel.refresh_token_hash == refresh_token_hash,
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, session: AuthSessionModel, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        await self.session.flush()

    async def revoke_session_chain(self, session: AuthSessionModel, revoked_at: datetime) -> None:
        session.revoked_at = session.revoked_at or revoked_at
        await self.session.execute(
            update(AuthSessionModel)
            .where(AuthSessionModel.user_id == session.user_id)
            .where(AuthSessionModel.tenant_id == session.tenant_id)
            .where(AuthSessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self.session.flush()

    async def revoke_all_for_user(self, user_id: UUID, revoked_at: datetime) -> None:
        await self.session.execute(
            update(AuthSessionModel)
            .where(AuthSessionModel.user_id == user_id)
            .where(AuthSessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        await self.session.flush()


class SQLAlchemyMfaMethodRepository(MfaMethodRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_and_type(
        self, user_id: UUID, method_type: MfaMethodType
    ) -> UserMfaMethodModel | None:
        result = await self.session.execute(
            select(UserMfaMethodModel).where(
                UserMfaMethodModel.user_id == user_id,
                UserMfaMethodModel.method_type == method_type,
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id_for_user(
        self, method_id: UUID, user_id: UUID, tenant_id: UUID
    ) -> UserMfaMethodModel | None:
        result = await self.session.execute(
            select(UserMfaMethodModel).where(
                UserMfaMethodModel.id == method_id,
                UserMfaMethodModel.user_id == user_id,
                UserMfaMethodModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: UUID, tenant_id: UUID) -> list[UserMfaMethodModel]:
        result = await self.session.execute(
            select(UserMfaMethodModel)
            .where(
                UserMfaMethodModel.user_id == user_id,
                UserMfaMethodModel.tenant_id == tenant_id,
            )
            .order_by(UserMfaMethodModel.method_type)
        )
        return list(result.scalars().all())

    async def list_active_for_user(
        self, user_id: UUID, tenant_id: UUID
    ) -> list[UserMfaMethodModel]:
        result = await self.session.execute(
            select(UserMfaMethodModel)
            .where(
                UserMfaMethodModel.user_id == user_id,
                UserMfaMethodModel.tenant_id == tenant_id,
                UserMfaMethodModel.status == MfaMethodStatus.ACTIVE,
                UserMfaMethodModel.disabled_at.is_(None),
            )
            .order_by(UserMfaMethodModel.is_primary.desc(), UserMfaMethodModel.method_type)
        )
        return list(result.scalars().all())

    async def save(self, method: UserMfaMethodModel) -> UserMfaMethodModel:
        self.session.add(method)
        await self.session.flush()
        return method

    async def unset_primary_for_user(self, user_id: UUID) -> None:
        await self.session.execute(
            update(UserMfaMethodModel)
            .where(UserMfaMethodModel.user_id == user_id)
            .values(is_primary=False)
        )
        await self.session.flush()

    async def disable_all_for_user(self, user_id: UUID, disabled_at: datetime) -> None:
        await self.session.execute(
            update(UserMfaMethodModel)
            .where(UserMfaMethodModel.user_id == user_id)
            .values(
                status=MfaMethodStatus.DISABLED,
                is_primary=False,
                disabled_at=disabled_at,
            )
        )
        await self.session.flush()


class SQLAlchemyMfaRecoveryCodeRepository(MfaRecoveryCodeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_many(self, codes: list[MfaRecoveryCodeModel]) -> list[MfaRecoveryCodeModel]:
        self.session.add_all(codes)
        await self.session.flush()
        return codes

    async def list_active_for_user(
        self, user_id: UUID, tenant_id: UUID
    ) -> list[MfaRecoveryCodeModel]:
        result = await self.session.execute(
            select(MfaRecoveryCodeModel).where(
                MfaRecoveryCodeModel.user_id == user_id,
                MfaRecoveryCodeModel.tenant_id == tenant_id,
                MfaRecoveryCodeModel.used_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def get_active_by_hash(
        self, user_id: UUID, tenant_id: UUID, code_hash: str
    ) -> MfaRecoveryCodeModel | None:
        result = await self.session.execute(
            select(MfaRecoveryCodeModel).where(
                MfaRecoveryCodeModel.user_id == user_id,
                MfaRecoveryCodeModel.tenant_id == tenant_id,
                MfaRecoveryCodeModel.code_hash == code_hash,
                MfaRecoveryCodeModel.used_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def invalidate_all_for_user(self, user_id: UUID, used_at: datetime) -> None:
        await self.session.execute(
            update(MfaRecoveryCodeModel)
            .where(MfaRecoveryCodeModel.user_id == user_id)
            .where(MfaRecoveryCodeModel.used_at.is_(None))
            .values(used_at=used_at)
        )
        await self.session.flush()


class SQLAlchemyTenantResolver(TenantResolver):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve_by_slug_or_code(self, tenant: str) -> UUID | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                (CompanyModel.slug == tenant) | (CompanyModel.code == tenant.upper()),
                CompanyModel.deleted_at.is_(None),
            )
        )
        company = result.scalar_one_or_none()
        if company is None:
            return None
        if company.status == CompanyStatus.SUSPENDED:
            raise TenantSuspendedError("Tenant suspended.")
        if company.status != CompanyStatus.ACTIVE or not company.is_active:
            raise TenantInactiveError("Tenant inactive.")
        return company.id
