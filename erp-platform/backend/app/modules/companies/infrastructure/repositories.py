from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.domain.repositories import CompanyRepository
from app.modules.companies.infrastructure.models import CompanyModel


class SQLAlchemyCompanyRepository(CompanyRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, company: CompanyModel) -> CompanyModel:
        self.session.add(company)
        await self.session.flush()
        return company

    async def get_by_id(self, company_id: UUID) -> CompanyModel | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.id == company_id,
                CompanyModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> CompanyModel | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.slug == slug,
                CompanyModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> CompanyModel | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.code == code,
                CompanyModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_document(self, document: str) -> CompanyModel | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                CompanyModel.document == document,
                CompanyModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def resolve_by_slug_or_code(self, value: str) -> CompanyModel | None:
        result = await self.session.execute(
            select(CompanyModel).where(
                or_(CompanyModel.slug == value.lower(), CompanyModel.code == value.upper()),
                CompanyModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        limit: int,
        offset: int,
        status: CompanyStatus | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> list[CompanyModel]:
        statement = self._filtered_select(status=status, is_active=is_active, search=search)
        statement = statement.order_by(CompanyModel.trade_name).limit(limit).offset(offset)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count(
        self,
        *,
        status: CompanyStatus | None = None,
        is_active: bool | None = None,
        search: str | None = None,
    ) -> int:
        statement = self._filtered_select(status=status, is_active=is_active, search=search)
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_slug(self, slug: str, exclude_id: UUID | None = None) -> bool:
        return await self._exists(CompanyModel.slug == slug, exclude_id=exclude_id)

    async def exists_by_code(self, code: str, exclude_id: UUID | None = None) -> bool:
        return await self._exists(CompanyModel.code == code, exclude_id=exclude_id)

    async def exists_by_document(self, document: str, exclude_id: UUID | None = None) -> bool:
        return await self._exists(CompanyModel.document == document, exclude_id=exclude_id)

    def _filtered_select(
        self,
        *,
        status: CompanyStatus | None,
        is_active: bool | None,
        search: str | None,
    ) -> Select[tuple[CompanyModel]]:
        statement = select(CompanyModel).where(CompanyModel.deleted_at.is_(None))
        if status is not None:
            statement = statement.where(CompanyModel.status == status)
        if is_active is not None:
            statement = statement.where(CompanyModel.is_active == is_active)
        if search:
            like = f"%{search.lower()}%"
            statement = statement.where(
                or_(
                    func.lower(CompanyModel.legal_name).like(like),
                    func.lower(CompanyModel.trade_name).like(like),
                    func.lower(CompanyModel.slug).like(like),
                    func.lower(CompanyModel.code).like(like),
                )
            )
        return statement

    async def _exists(self, condition, *, exclude_id: UUID | None = None) -> bool:
        statement = select(CompanyModel.id).where(condition, CompanyModel.deleted_at.is_(None))
        if exclude_id is not None:
            statement = statement.where(CompanyModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None
