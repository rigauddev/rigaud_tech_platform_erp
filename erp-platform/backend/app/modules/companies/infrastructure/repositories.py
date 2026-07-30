from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.companies.domain.entities import BranchStatus, CompanyStatus, MembershipStatus
from app.modules.companies.domain.exceptions import ContextSelectionError
from app.modules.companies.domain.repositories import (
    BranchRepository,
    CompanyRepository,
    MembershipRepository,
)
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)


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


class SQLAlchemyBranchRepository(BranchRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, branch: BranchModel) -> BranchModel:
        self.session.add(branch)
        await self.session.flush()
        return branch

    async def get_by_id(self, branch_id: UUID) -> BranchModel | None:
        result = await self.session.execute(
            select(BranchModel).where(
                BranchModel.id == branch_id,
                BranchModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(
        self,
        tenant_id: UUID,
        *,
        limit: int,
        offset: int,
        status: BranchStatus | None = None,
    ) -> list[BranchModel]:
        statement = select(BranchModel).where(
            BranchModel.tenant_id == tenant_id,
            BranchModel.deleted_at.is_(None),
        )
        if status is not None:
            statement = statement.where(BranchModel.status == status)
        statement = statement.order_by(BranchModel.is_headquarters.desc(), BranchModel.name)
        result = await self.session.execute(statement.limit(limit).offset(offset))
        return list(result.scalars().all())

    async def count_by_tenant(self, tenant_id: UUID, status: BranchStatus | None = None) -> int:
        statement = select(BranchModel.id).where(
            BranchModel.tenant_id == tenant_id,
            BranchModel.deleted_at.is_(None),
        )
        if status is not None:
            statement = statement.where(BranchModel.status == status)
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def exists_by_code(
        self, tenant_id: UUID, code: str, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(BranchModel.id).where(
            BranchModel.tenant_id == tenant_id,
            BranchModel.code == code,
            BranchModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(BranchModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    async def exists_by_document(
        self, tenant_id: UUID, document: str, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(BranchModel.id).where(
            BranchModel.tenant_id == tenant_id,
            BranchModel.document == document,
            BranchModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(BranchModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None

    async def has_headquarters(self, tenant_id: UUID, exclude_id: UUID | None = None) -> bool:
        statement = select(BranchModel.id).where(
            BranchModel.tenant_id == tenant_id,
            BranchModel.is_headquarters.is_(True),
            BranchModel.deleted_at.is_(None),
        )
        if exclude_id is not None:
            statement = statement.where(BranchModel.id != exclude_id)
        result = await self.session.execute(statement.limit(1))
        return result.scalar_one_or_none() is not None


class SQLAlchemyMembershipRepository(MembershipRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_company_membership(
        self, membership: CompanyMembershipModel
    ) -> CompanyMembershipModel:
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def add_branch_membership(
        self, membership: BranchMembershipModel
    ) -> BranchMembershipModel:
        await self._ensure_branch_membership_same_tenant(membership)
        self.session.add(membership)
        await self.session.flush()
        return membership

    async def get_company_membership(
        self, user_id: UUID, tenant_id: UUID
    ) -> CompanyMembershipModel | None:
        result = await self.session.execute(
            select(CompanyMembershipModel).where(
                CompanyMembershipModel.user_id == user_id,
                CompanyMembershipModel.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_default_company_membership(self, user_id: UUID) -> CompanyMembershipModel | None:
        result = await self.session.execute(
            select(CompanyMembershipModel).where(
                CompanyMembershipModel.user_id == user_id,
                CompanyMembershipModel.is_default.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_company_memberships(
        self, user_id: UUID, status: MembershipStatus | None = None
    ) -> list[CompanyMembershipModel]:
        statement = select(CompanyMembershipModel).where(CompanyMembershipModel.user_id == user_id)
        if status is not None:
            statement = statement.where(CompanyMembershipModel.status == status)
        result = await self.session.execute(
            statement.order_by(
                CompanyMembershipModel.is_default.desc(), CompanyMembershipModel.created_at
            )
        )
        return list(result.scalars().all())

    async def get_branch_membership(
        self, company_membership_id: UUID, branch_id: UUID
    ) -> BranchMembershipModel | None:
        result = await self.session.execute(
            select(BranchMembershipModel)
            .join(
                CompanyMembershipModel,
                CompanyMembershipModel.id == BranchMembershipModel.company_membership_id,
            )
            .join(BranchModel, BranchModel.id == BranchMembershipModel.branch_id)
            .where(
                BranchMembershipModel.company_membership_id == company_membership_id,
                BranchMembershipModel.branch_id == branch_id,
                BranchModel.tenant_id == CompanyMembershipModel.tenant_id,
                BranchModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_default_branch_membership(
        self, company_membership_id: UUID
    ) -> BranchMembershipModel | None:
        result = await self.session.execute(
            select(BranchMembershipModel)
            .join(
                CompanyMembershipModel,
                CompanyMembershipModel.id == BranchMembershipModel.company_membership_id,
            )
            .join(BranchModel, BranchModel.id == BranchMembershipModel.branch_id)
            .where(
                BranchMembershipModel.company_membership_id == company_membership_id,
                BranchMembershipModel.is_default.is_(True),
                BranchModel.tenant_id == CompanyMembershipModel.tenant_id,
                BranchModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_branch_memberships(
        self,
        company_membership_id: UUID,
        status: MembershipStatus | None = None,
    ) -> list[BranchMembershipModel]:
        statement = (
            select(BranchMembershipModel)
            .join(
                CompanyMembershipModel,
                CompanyMembershipModel.id == BranchMembershipModel.company_membership_id,
            )
            .join(BranchModel, BranchModel.id == BranchMembershipModel.branch_id)
            .where(
                BranchMembershipModel.company_membership_id == company_membership_id,
                BranchModel.tenant_id == CompanyMembershipModel.tenant_id,
                BranchModel.deleted_at.is_(None),
            )
        )
        if status is not None:
            statement = statement.where(BranchMembershipModel.status == status)
        result = await self.session.execute(
            statement.order_by(
                BranchMembershipModel.is_default.desc(), BranchMembershipModel.created_at
            )
        )
        return list(result.scalars().all())

    async def _ensure_branch_membership_same_tenant(
        self, membership: BranchMembershipModel
    ) -> None:
        company_membership_tenant_id = (
            await self.session.execute(
                select(CompanyMembershipModel.tenant_id).where(
                    CompanyMembershipModel.id == membership.company_membership_id
                )
            )
        ).scalar_one_or_none()
        branch_tenant_id = (
            await self.session.execute(
                select(BranchModel.tenant_id).where(
                    BranchModel.id == membership.branch_id,
                    BranchModel.deleted_at.is_(None),
                )
            )
        ).scalar_one_or_none()
        if (
            company_membership_tenant_id is None
            or branch_tenant_id is None
            or company_membership_tenant_id != branch_tenant_id
        ):
            raise ContextSelectionError("Branch membership tenant mismatch.")
