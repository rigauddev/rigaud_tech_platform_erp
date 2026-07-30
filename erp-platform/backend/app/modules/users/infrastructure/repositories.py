from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.infrastructure.models import AuthUserModel
from app.modules.users.domain.entities import UserStatus
from app.modules.users.domain.repositories import UserRepository


class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, user: AuthUserModel) -> AuthUserModel:
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> AuthUserModel | None:
        result = await self.session.execute(
            select(AuthUserModel).where(
                AuthUserModel.id == user_id,
                AuthUserModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email_and_tenant_id(self, email: str, tenant_id: UUID) -> AuthUserModel | None:
        result = await self.session.execute(
            select(AuthUserModel).where(
                AuthUserModel.email == email,
                AuthUserModel.tenant_id == tenant_id,
                AuthUserModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        tenant_id: UUID | None = None,
        status: UserStatus | None = None,
        search: str | None = None,
    ) -> list[AuthUserModel]:
        statement = self._filtered_select(tenant_id=tenant_id, status=status, search=search)
        statement = statement.order_by(AuthUserModel.email).limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        tenant_id: UUID | None = None,
        status: UserStatus | None = None,
        search: str | None = None,
    ) -> int:
        statement = self._filtered_select(tenant_id=tenant_id, status=status, search=search)
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_email_and_tenant_id(
        self,
        email: str,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement = select(AuthUserModel.id).where(
            AuthUserModel.email == email,
            AuthUserModel.tenant_id == tenant_id,
            AuthUserModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(AuthUserModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    def _filtered_select(
        self,
        *,
        tenant_id: UUID | None,
        status: UserStatus | None,
        search: str | None,
    ) -> Select[tuple[AuthUserModel]]:
        statement = select(AuthUserModel).where(AuthUserModel.deleted_at.is_(None))
        if tenant_id is not None:
            statement = statement.where(AuthUserModel.tenant_id == tenant_id)
        if status is not None:
            statement = statement.where(AuthUserModel.status == status)
        if search:
            like = f"%{search.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(AuthUserModel.email).like(like),
                    func.lower(AuthUserModel.first_name).like(like),
                    func.lower(AuthUserModel.last_name).like(like),
                    func.lower(AuthUserModel.display_name).like(like),
                )
            )
        return statement
