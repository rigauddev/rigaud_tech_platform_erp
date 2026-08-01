from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.companies.domain.entities import (
    AccessScope,
    BranchRole,
    CompanyRole,
    MembershipStatus,
)
from app.modules.companies.domain.exceptions import ContextSelectionError
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)
from app.modules.companies.infrastructure.repositories import SQLAlchemyMembershipRepository


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture(autouse=True)
async def clean_tables() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()
    yield
    async with async_session_factory() as session:
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()


def valid_cnpj(seed: int) -> str:
    base = f"{seed:08d}0001"[-12:]

    def digit(value: str, weights: list[int]) -> str:
        total = sum(int(item) * weight for item, weight in zip(value, weights, strict=True))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    first = digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = digit(base + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return base + first + second


async def create_platform_admin() -> AuthUserModel:
    company = CompanyModel(
        id=uuid4(),
        legal_name="Platform Admin Ltda",
        trade_name="Platform Admin",
        document=valid_cnpj(10),
        email="admin@platform.test",
        phone="75982165869",
        slug="platform-admin",
        code="PLATFORM",
        is_active=True,
    )
    user = AuthUserModel(
        tenant_id=company.id,
        tenant_slug=company.slug,
        email="admin@platform.test",
        password_hash=PasswordService().hash("Senha123"),
        is_active=True,
        is_superuser=True,
    )
    async with async_session_factory() as session:
        session.add(company)
        await session.flush()
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


def auth_header(user: AuthUserModel) -> dict[str, str]:
    token = TokenService().create_access_token(user.id, user.tenant_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_company_creation_creates_headquarters_and_user_context(
    client: AsyncClient,
) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Rigaud Restaurante Ltda",
            "trade_name": "Rigaud Restaurante",
            "document": valid_cnpj(11),
            "email": "contato@rigaud.test",
            "phone": "75982165869",
            "slug": "rigaud-restaurante",
            "code": "RIGREST",
            "timezone": "America/Sao_Paulo",
            "locale": "pt-BR",
            "currency": "BRL",
        },
    )
    assert company_response.status_code == 201
    tenant_id = company_response.json()["id"]

    branches_response = await client.get(
        "/api/v1/companies/branches",
        headers=headers,
        params={"company_id": tenant_id},
    )
    assert branches_response.status_code == 200
    headquarters = branches_response.json()["items"][0]
    assert headquarters["branch_type"] == "headquarters"
    assert headquarters["is_headquarters"] is True

    user_response = await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "email": "manager@rigaud.test",
            "password": "Senha123",
            "first_name": "Gerente",
            "must_change_password": False,
        },
    )
    assert user_response.status_code == 201

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "manager@rigaud.test",
            "password": "Senha123",
        },
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    me_response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    me = me_response.json()
    assert me["tenant_id"] == tenant_id
    assert me["branch_id"] == headquarters["id"]
    assert me["access_scope"] == "selected_branches"

    context_response = await client.get(
        "/api/v1/auth/context",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert context_response.status_code == 200
    assert (
        context_response.json()["memberships"][0]["branches"][0]["branch_id"] == headquarters["id"]
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_cannot_switch_to_unauthorized_branch(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Tenant A Ltda",
            "trade_name": "Tenant A",
            "document": valid_cnpj(12),
            "slug": "tenant-a-context",
            "code": "TENCTX",
        },
    )
    tenant_id = company_response.json()["id"]
    branches = await client.get(
        "/api/v1/companies/branches",
        headers=headers,
        params={"company_id": tenant_id},
    )
    default_branch_id = branches.json()["items"][0]["id"]
    second_branch = await client.post(
        "/api/v1/companies/branches",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "code": "STORE2",
            "name": "Loja 2",
            "branch_type": "store",
        },
    )
    assert second_branch.status_code == 201

    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "email": "operator@tenant.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "operator@tenant.test",
            "password": "Senha123",
        },
    )
    token = login_response.json()["access_token"]

    allowed = await client.post(
        "/api/v1/auth/context/switch",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": tenant_id, "branch_id": default_branch_id},
    )
    assert allowed.status_code == 403
    assert allowed.json()["code"] == "CONTEXT_NOT_ALLOWED"

    denied = await client.post(
        "/api/v1/auth/context/switch",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": tenant_id, "branch_id": second_branch.json()["id"]},
    )
    assert denied.status_code == 403
    assert denied.json()["code"] == "CONTEXT_NOT_ALLOWED"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_can_switch_to_authorized_second_company(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    first_company = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Tenant Multi A Ltda",
            "trade_name": "Tenant Multi A",
            "document": valid_cnpj(13),
            "slug": "tenant-multi-a",
            "code": "MULTIA",
        },
    )
    second_company = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Tenant Multi B Ltda",
            "trade_name": "Tenant Multi B",
            "document": valid_cnpj(14),
            "slug": "tenant-multi-b",
            "code": "MULTIB",
        },
    )
    first_tenant_id = first_company.json()["id"]
    second_tenant_id = second_company.json()["id"]

    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": first_tenant_id,
            "email": "multi@tenant.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )

    async with async_session_factory() as session:
        user = (
            await session.execute(
                select(AuthUserModel).where(AuthUserModel.email == "multi@tenant.test")
            )
        ).scalar_one()
        second_branch = (
            await session.execute(
                select(BranchModel).where(
                    BranchModel.tenant_id == second_tenant_id,
                    BranchModel.is_headquarters.is_(True),
                )
            )
        ).scalar_one()
        membership = await SQLAlchemyMembershipRepository(session).add_company_membership(
            CompanyMembershipModel(
                user_id=user.id,
                tenant_id=second_branch.tenant_id,
                role=CompanyRole.MEMBER,
                status=MembershipStatus.ACTIVE,
                access_scope=AccessScope.SELECTED_BRANCHES,
                is_default=False,
                created_by=admin.id,
                updated_by=admin.id,
            )
        )
        await SQLAlchemyMembershipRepository(session).add_branch_membership(
            BranchMembershipModel(
                company_membership_id=membership.id,
                branch_id=second_branch.id,
                role=BranchRole.BRANCH_OPERATOR,
                status=MembershipStatus.ACTIVE,
                is_default=True,
                created_by=admin.id,
                updated_by=admin.id,
            )
        )
        await session.commit()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "multi@tenant.test",
            "password": "Senha123",
        },
    )
    token = login_response.json()["access_token"]

    switch_response = await client.post(
        "/api/v1/auth/context/switch",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": second_tenant_id, "branch_id": str(second_branch.id)},
    )
    assert switch_response.status_code == 403
    assert switch_response.json()["code"] == "CONTEXT_NOT_ALLOWED"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_branch_membership_rejects_cross_tenant_link(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    first_company = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Cross Tenant A Ltda",
            "trade_name": "Cross Tenant A",
            "document": valid_cnpj(15),
            "slug": "cross-tenant-a",
            "code": "CROSSA",
        },
    )
    second_company = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Cross Tenant B Ltda",
            "trade_name": "Cross Tenant B",
            "document": valid_cnpj(16),
            "slug": "cross-tenant-b",
            "code": "CROSSB",
        },
    )
    first_tenant_id = first_company.json()["id"]
    second_tenant_id = second_company.json()["id"]

    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": first_tenant_id,
            "email": "cross@tenant.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )

    async with async_session_factory() as session:
        user = (
            await session.execute(
                select(AuthUserModel).where(AuthUserModel.email == "cross@tenant.test")
            )
        ).scalar_one()
        first_membership = (
            await session.execute(
                select(CompanyMembershipModel).where(
                    CompanyMembershipModel.user_id == user.id,
                    CompanyMembershipModel.tenant_id == first_tenant_id,
                )
            )
        ).scalar_one()
        second_branch = (
            await session.execute(
                select(BranchModel).where(
                    BranchModel.tenant_id == second_tenant_id,
                    BranchModel.is_headquarters.is_(True),
                )
            )
        ).scalar_one()

        with pytest.raises(ContextSelectionError):
            await SQLAlchemyMembershipRepository(session).add_branch_membership(
                BranchMembershipModel(
                    company_membership_id=first_membership.id,
                    branch_id=second_branch.id,
                    role=BranchRole.BRANCH_OPERATOR,
                    status=MembershipStatus.ACTIVE,
                    is_default=False,
                    created_by=admin.id,
                    updated_by=admin.id,
                )
            )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_revalidates_inactive_membership(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Refresh Context Ltda",
            "trade_name": "Refresh Context",
            "document": valid_cnpj(17),
            "slug": "refresh-context",
            "code": "REFCTX",
        },
    )
    tenant_id = company_response.json()["id"]
    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "email": "refresh@tenant.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "refresh@tenant.test",
            "password": "Senha123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    async with async_session_factory() as session:
        user = (
            await session.execute(
                select(AuthUserModel).where(AuthUserModel.email == "refresh@tenant.test")
            )
        ).scalar_one()
        membership = (
            await session.execute(
                select(CompanyMembershipModel).where(
                    CompanyMembershipModel.user_id == user.id,
                    CompanyMembershipModel.tenant_id == tenant_id,
                )
            )
        ).scalar_one()
        membership.status = MembershipStatus.INACTIVE
        await session.commit()

    refresh_response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 401
    assert refresh_response.json()["code"] == "AUTH_TOKEN_INVALID"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_all_branches_context_can_switch_without_branch(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "All Branches Ltda",
            "trade_name": "All Branches",
            "document": valid_cnpj(18),
            "slug": "all-branches",
            "code": "ALLBR",
        },
    )
    tenant_id = company_response.json()["id"]
    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "email": "allbranches@tenant.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )

    async with async_session_factory() as session:
        user = (
            await session.execute(
                select(AuthUserModel).where(AuthUserModel.email == "allbranches@tenant.test")
            )
        ).scalar_one()
        membership = (
            await session.execute(
                select(CompanyMembershipModel).where(
                    CompanyMembershipModel.user_id == user.id,
                    CompanyMembershipModel.tenant_id == tenant_id,
                )
            )
        ).scalar_one()
        membership.access_scope = AccessScope.ALL_BRANCHES
        await session.commit()

    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "allbranches@tenant.test",
            "password": "Senha123",
        },
    )
    token = login_response.json()["access_token"]

    switch_response = await client.post(
        "/api/v1/auth/context/switch",
        headers={"Authorization": f"Bearer {token}"},
        json={"tenant_id": tenant_id, "branch_id": None},
    )
    assert switch_response.status_code == 403
    assert switch_response.json()["code"] == "CONTEXT_NOT_ALLOWED"
