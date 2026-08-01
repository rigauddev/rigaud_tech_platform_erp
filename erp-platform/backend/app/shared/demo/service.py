from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.infrastructure.models import (
    AuthSessionModel,
    AuthUserModel,
    MfaRecoveryCodeModel,
    UserMfaMethodModel,
)
from app.modules.categories.domain.entities import CategoryStatus
from app.modules.categories.infrastructure.models import CategoryModel
from app.modules.companies.domain.entities import (
    AccessScope,
    BranchRole,
    BranchStatus,
    CompanyRole,
    CompanyStatus,
    MembershipStatus,
)
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)
from app.modules.products.domain.entities import ProductStatus
from app.modules.products.infrastructure.models import ProductModel
from app.modules.users.domain.entities import UserStatus
from app.shared.demo.data import (
    DEMO_PASSWORD,
    PLATFORM_COMPANY,
    PLATFORM_USERS,
    RESETTABLE_TENANT_SLUGS,
    RESTAURANT_BRANCHES,
    RESTAURANT_CATEGORIES,
    RESTAURANT_COMPANY,
    RESTAURANT_USERS,
    RETAIL_BRANCHES,
    RETAIL_CATEGORIES,
    RETAIL_COMPANY,
    RETAIL_USERS,
    DemoBranch,
    DemoCategory,
    DemoCompany,
    DemoProduct,
    DemoUser,
    restaurant_products,
    retail_products,
)


@dataclass
class DemoSeedSummary:
    mode: str
    companies: int = 0
    branches: int = 0
    users: int = 0
    memberships: int = 0
    branch_memberships: int = 0
    categories: int = 0
    products: int = 0
    deleted_rows: int = 0

    def as_dict(self) -> dict[str, int | str]:
        return asdict(self)


class DemoSeeder:
    def __init__(self, session: AsyncSession, password: str = DEMO_PASSWORD) -> None:
        self.session = session
        self.password_hash = PasswordService().hash(password)

    async def seed_all(self) -> DemoSeedSummary:
        await self.seed_platform()
        restaurant = await self.seed_restaurant()
        retail = await self.seed_retail()
        return DemoSeedSummary(
            mode="all",
            companies=1 + restaurant.companies + retail.companies,
            branches=restaurant.branches + retail.branches,
            users=len(PLATFORM_USERS) + restaurant.users + retail.users,
            memberships=len(PLATFORM_USERS) + restaurant.memberships + retail.memberships,
            branch_memberships=restaurant.branch_memberships + retail.branch_memberships,
            categories=restaurant.categories + retail.categories,
            products=restaurant.products + retail.products,
        )

    async def seed_platform(self) -> DemoSeedSummary:
        company = await self._ensure_company(PLATFORM_COMPANY)
        users = await self._ensure_users(company, PLATFORM_USERS)
        await self.session.commit()
        return DemoSeedSummary(
            mode="platform",
            companies=1,
            users=len(users),
            memberships=len(users),
        )

    async def seed_restaurant(self) -> DemoSeedSummary:
        company = await self._ensure_company(RESTAURANT_COMPANY)
        branches = await self._ensure_branches(company, RESTAURANT_BRANCHES)
        users = await self._ensure_users(company, RESTAURANT_USERS)
        branch_memberships = await self._ensure_branch_memberships(users, branches)
        categories = await self._ensure_categories(company.id, RESTAURANT_CATEGORIES)
        products = await self._ensure_products(company.id, restaurant_products())
        await self.session.commit()
        return DemoSeedSummary(
            mode="restaurant",
            companies=1,
            branches=len(branches),
            users=len(users),
            memberships=len(users),
            branch_memberships=branch_memberships,
            categories=len(categories),
            products=len(products),
        )

    async def seed_retail(self) -> DemoSeedSummary:
        company = await self._ensure_company(RETAIL_COMPANY)
        branches = await self._ensure_branches(company, RETAIL_BRANCHES)
        users = await self._ensure_users(company, RETAIL_USERS)
        branch_memberships = await self._ensure_branch_memberships(users, branches)
        categories = await self._ensure_categories(company.id, RETAIL_CATEGORIES)
        products = await self._ensure_products(company.id, retail_products())
        await self.session.commit()
        return DemoSeedSummary(
            mode="retail",
            companies=1,
            branches=len(branches),
            users=len(users),
            memberships=len(users),
            branch_memberships=branch_memberships,
            categories=len(categories),
            products=len(products),
        )

    async def reset(self) -> DemoSeedSummary:
        tenant_ids = (
            (
                await self.session.execute(
                    select(CompanyModel.id).where(CompanyModel.slug.in_(RESETTABLE_TENANT_SLUGS))
                )
            )
            .scalars()
            .all()
        )
        if not tenant_ids:
            return DemoSeedSummary(mode="reset")

        user_ids = (
            (
                await self.session.execute(
                    select(AuthUserModel.id).where(AuthUserModel.tenant_id.in_(tenant_ids))
                )
            )
            .scalars()
            .all()
        )
        membership_ids = (
            (
                await self.session.execute(
                    select(CompanyMembershipModel.id).where(
                        CompanyMembershipModel.tenant_id.in_(tenant_ids)
                    )
                )
            )
            .scalars()
            .all()
        )

        deleted_rows = 0
        deleted_rows += await self._delete_where(
            AuthSessionModel, AuthSessionModel.tenant_id.in_(tenant_ids)
        )
        deleted_rows += await self._delete_where(
            UserMfaMethodModel, UserMfaMethodModel.tenant_id.in_(tenant_ids)
        )
        deleted_rows += await self._delete_where(
            MfaRecoveryCodeModel, MfaRecoveryCodeModel.tenant_id.in_(tenant_ids)
        )
        if membership_ids:
            deleted_rows += await self._delete_where(
                BranchMembershipModel,
                BranchMembershipModel.company_membership_id.in_(membership_ids),
            )
        deleted_rows += await self._delete_where(
            CompanyMembershipModel,
            CompanyMembershipModel.tenant_id.in_(tenant_ids),
        )
        deleted_rows += await self._delete_where(
            ProductModel, ProductModel.tenant_id.in_(tenant_ids)
        )
        deleted_rows += await self._delete_where(
            CategoryModel, CategoryModel.tenant_id.in_(tenant_ids)
        )
        deleted_rows += await self._delete_where(BranchModel, BranchModel.tenant_id.in_(tenant_ids))
        if user_ids:
            deleted_rows += await self._delete_where(AuthUserModel, AuthUserModel.id.in_(user_ids))
        deleted_rows += await self._delete_where(CompanyModel, CompanyModel.id.in_(tenant_ids))
        await self.session.commit()
        return DemoSeedSummary(mode="reset", deleted_rows=deleted_rows)

    async def _ensure_company(self, data: DemoCompany) -> CompanyModel:
        company = (
            await self.session.execute(select(CompanyModel).where(CompanyModel.slug == data.slug))
        ).scalar_one_or_none()
        if company is None:
            company = CompanyModel()
            self.session.add(company)

        company.legal_name = data.legal_name
        company.trade_name = data.trade_name
        company.document = data.document
        company.email = data.email
        company.phone = data.phone
        company.slug = data.slug
        company.code = data.code
        company.status = CompanyStatus.ACTIVE
        company.timezone = "America/Sao_Paulo"
        company.locale = "pt-BR"
        company.currency = "BRL"
        company.is_active = True
        company.deleted_at = None
        await self.session.flush()
        return company

    async def _ensure_branches(
        self,
        company: CompanyModel,
        branches: Iterable[DemoBranch],
    ) -> list[BranchModel]:
        models: list[BranchModel] = []
        for data in branches:
            branch = (
                await self.session.execute(
                    select(BranchModel).where(
                        BranchModel.tenant_id == company.id,
                        BranchModel.code == data.code,
                    )
                )
            ).scalar_one_or_none()
            if branch is None:
                branch = BranchModel(tenant_id=company.id, code=data.code)
                self.session.add(branch)

            branch.name = data.name
            branch.legal_name = company.legal_name
            branch.trade_name = data.name
            branch.document = company.document if data.is_headquarters else None
            branch.branch_type = data.branch_type
            branch.status = BranchStatus.ACTIVE
            branch.is_headquarters = data.is_headquarters
            branch.timezone = "America/Sao_Paulo"
            branch.email = data.email
            branch.phone = data.phone
            branch.address = data.address
            branch.deleted_at = None
            models.append(branch)
        await self.session.flush()
        return models

    async def _ensure_users(
        self,
        company: CompanyModel,
        users: Iterable[DemoUser],
    ) -> list[AuthUserModel]:
        models: list[AuthUserModel] = []
        for data in users:
            user = (
                await self.session.execute(
                    select(AuthUserModel).where(
                        AuthUserModel.tenant_id == company.id,
                        func.lower(AuthUserModel.email) == data.email.lower(),
                    )
                )
            ).scalar_one_or_none()
            if user is None:
                user = AuthUserModel(
                    tenant_id=company.id,
                    tenant_slug=company.slug,
                    email=data.email.lower(),
                    password_hash=self.password_hash,
                )
                self.session.add(user)

            user.tenant_slug = company.slug
            user.first_name = data.first_name
            user.last_name = data.last_name
            user.display_name = data.display_name
            user.phone = data.phone
            user.status = UserStatus.ACTIVE
            user.is_active = True
            user.is_superuser = data.is_superuser
            user.must_change_password = False
            user.deleted_at = None
            await self.session.flush()
            await self._ensure_company_membership(company, user, data.company_role)
            models.append(user)
        return models

    async def _ensure_company_membership(
        self,
        company: CompanyModel,
        user: AuthUserModel,
        role: CompanyRole,
    ) -> CompanyMembershipModel:
        membership = (
            await self.session.execute(
                select(CompanyMembershipModel).where(
                    CompanyMembershipModel.user_id == user.id,
                    CompanyMembershipModel.tenant_id == company.id,
                )
            )
        ).scalar_one_or_none()
        if membership is None:
            membership = CompanyMembershipModel(user_id=user.id, tenant_id=company.id)
            self.session.add(membership)
        membership.role = role
        membership.status = MembershipStatus.ACTIVE
        membership.access_scope = AccessScope.ALL_BRANCHES
        membership.is_default = True
        await self.session.flush()
        return membership

    async def _ensure_branch_memberships(
        self,
        users: Iterable[AuthUserModel],
        branches: Iterable[BranchModel],
    ) -> int:
        count = 0
        branch_list = list(branches)
        for user in users:
            membership = (
                await self.session.execute(
                    select(CompanyMembershipModel).where(
                        CompanyMembershipModel.user_id == user.id,
                        CompanyMembershipModel.tenant_id == user.tenant_id,
                    )
                )
            ).scalar_one()
            for index, branch in enumerate(branch_list):
                branch_membership = (
                    await self.session.execute(
                        select(BranchMembershipModel).where(
                            BranchMembershipModel.company_membership_id == membership.id,
                            BranchMembershipModel.branch_id == branch.id,
                        )
                    )
                ).scalar_one_or_none()
                if branch_membership is None:
                    branch_membership = BranchMembershipModel(
                        company_membership_id=membership.id,
                        branch_id=branch.id,
                    )
                    self.session.add(branch_membership)
                branch_membership.role = (
                    BranchRole.BRANCH_MANAGER
                    if membership.role == CompanyRole.COMPANY_ADMIN
                    else BranchRole.BRANCH_OPERATOR
                )
                branch_membership.status = MembershipStatus.ACTIVE
                branch_membership.is_default = index == 0
                count += 1
        await self.session.flush()
        return count

    async def _ensure_categories(
        self,
        tenant_id: UUID,
        categories: Iterable[DemoCategory],
    ) -> list[CategoryModel]:
        models: list[CategoryModel] = []
        for data in categories:
            category = (
                await self.session.execute(
                    select(CategoryModel).where(
                        CategoryModel.tenant_id == tenant_id,
                        CategoryModel.internal_code == data.internal_code,
                    )
                )
            ).scalar_one_or_none()
            if category is None:
                category = CategoryModel(tenant_id=tenant_id, internal_code=data.internal_code)
                self.session.add(category)

            category.parent_id = None
            category.name = data.name
            category.slug = data.slug
            category.description = data.description
            category.icon = data.icon
            category.color = data.color
            category.display_order = data.display_order
            category.status = CategoryStatus.ACTIVE
            category.is_active = True
            category.deleted_at = None
            models.append(category)
        await self.session.flush()
        return models

    async def _ensure_products(
        self,
        tenant_id: UUID,
        products: Iterable[DemoProduct],
    ) -> list[ProductModel]:
        models: list[ProductModel] = []
        for data in products:
            product = (
                await self.session.execute(
                    select(ProductModel).where(
                        ProductModel.tenant_id == tenant_id,
                        ProductModel.internal_code == data.internal_code,
                    )
                )
            ).scalar_one_or_none()
            if product is None:
                product = ProductModel(tenant_id=tenant_id, internal_code=data.internal_code)
                self.session.add(product)

            product.name = data.name
            product.description = data.description
            product.barcode = None
            product.product_type = data.product_type
            product.unit_of_measure = data.unit_of_measure
            product.status = ProductStatus.ACTIVE
            product.sale_price = data.sale_price
            product.cost_price = data.cost_price
            product.main_image_url = None
            product.is_active = True
            product.is_available_for_sale = True
            product.deleted_at = None
            models.append(product)
        await self.session.flush()
        return models

    async def _delete_where(self, model: type, *criteria: object) -> int:
        result = await self.session.execute(delete(model).where(*criteria))
        return result.rowcount or 0
