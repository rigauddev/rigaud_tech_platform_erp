from datetime import UTC, datetime
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
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel
from app.modules.users.domain.entities import UserStatus


@pytest_asyncio.fixture
async def users_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


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


async def create_company(
    *,
    slug: str,
    code: str,
    document_seed: int,
    status: CompanyStatus = CompanyStatus.ACTIVE,
    is_active: bool = True,
) -> CompanyModel:
    company = CompanyModel(
        id=uuid4(),
        legal_name=f"{slug} Ltda",
        trade_name=slug,
        document=valid_cnpj(document_seed),
        email=f"contato@{slug}.com.br",
        phone="75982165869",
        slug=slug,
        code=code,
        status=status,
        timezone="America/Sao_Paulo",
        locale="pt-BR",
        currency="BRL",
        is_active=is_active,
    )
    async with async_session_factory() as session:
        session.add(company)
        await session.commit()
        await session.refresh(company)
    return company


async def create_user(
    company: CompanyModel,
    *,
    email: str,
    password: str = "Senha123",
    is_superuser: bool = False,
    status: UserStatus = UserStatus.ACTIVE,
) -> AuthUserModel:
    user = AuthUserModel(
        tenant_id=company.id,
        tenant_slug=company.slug,
        email=email.lower(),
        password_hash=PasswordService().hash(password),
        first_name="User",
        last_name="Test",
        status=status,
        is_active=status == UserStatus.ACTIVE,
        is_superuser=is_superuser,
    )
    async with async_session_factory() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


def auth_header(user: AuthUserModel) -> dict[str, str]:
    token = TokenService().create_access_token(user.id, user.tenant_id)
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.asyncio
async def test_superuser_can_manage_users(users_client: AsyncClient) -> None:
    admin_company = await create_company(slug="admin-company", code="ADMIN", document_seed=1)
    target_company = await create_company(slug="target-company", code="TARGET", document_seed=2)
    admin = await create_user(admin_company, email="admin@example.com", is_superuser=True)
    headers = auth_header(admin)

    created = await users_client.post(
        "/api/v1/users",
        json={
            "tenant_id": str(target_company.id),
            "email": " New.User@Example.com ",
            "password": "Senha123",
            "first_name": "New",
            "last_name": "User",
            "display_name": "New User",
            "phone": "75982165869",
        },
        headers=headers,
    )
    assert created.status_code == 201
    user_id = created.json()["id"]
    assert created.json()["email"] == "new.user@example.com"
    assert created.json()["tenant_id"] == str(target_company.id)
    assert "password_hash" not in created.text

    listed = await users_client.get(
        "/api/v1/users",
        params={"company_id": str(target_company.id), "search": "new.user"},
        headers=headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = await users_client.patch(
        f"/api/v1/users/{user_id}",
        json={"display_name": "Updated User", "status": "inactive"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Updated User"
    assert updated.json()["status"] == "inactive"
    assert updated.json()["is_active"] is False

    activated = await users_client.post(f"/api/v1/users/{user_id}/activate", headers=headers)
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    reset = await users_client.post(
        f"/api/v1/users/{user_id}/reset-password",
        json={"temporary_password": "NovaSenha123"},
        headers=headers,
    )
    assert reset.status_code == 200

    async with async_session_factory() as session:
        user = await session.get(AuthUserModel, user_id)
        assert user is not None
        assert user.must_change_password is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_common_user_can_only_manage_own_profile(users_client: AsyncClient) -> None:
    company = await create_company(slug="tenant-one", code="TENANT1", document_seed=3)
    user = await create_user(company, email="common@example.com")
    headers = auth_header(user)

    list_response = await users_client.get("/api/v1/users", headers=headers)
    assert list_response.status_code == 403

    me = await users_client.get("/api/v1/users/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["id"] == str(user.id)

    updated = await users_client.patch(
        "/api/v1/users/me",
        json={"display_name": "Common Updated", "phone": "75982165869"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["display_name"] == "Common Updated"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_duplicate_email_is_global_for_login(users_client: AsyncClient) -> None:
    company_one = await create_company(slug="company-one", code="COMP1", document_seed=4)
    company_two = await create_company(slug="company-two", code="COMP2", document_seed=5)
    admin = await create_user(company_one, email="admin@example.com", is_superuser=True)
    await create_user(company_one, email="same@example.com")
    headers = auth_header(admin)

    duplicate = await users_client.post(
        "/api/v1/users",
        json={
            "tenant_id": str(company_one.id),
            "email": "same@example.com",
            "password": "Senha123",
        },
        headers=headers,
    )
    allowed = await users_client.post(
        "/api/v1/users",
        json={
            "tenant_id": str(company_two.id),
            "email": "same@example.com",
            "password": "Senha123",
        },
        headers=headers,
    )

    assert duplicate.status_code == 409
    assert allowed.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_block_revokes_sessions_and_blocks_login(users_client: AsyncClient) -> None:
    company = await create_company(slug="block-company", code="BLOCK", document_seed=6)
    admin = await create_user(company, email="admin@example.com", is_superuser=True)
    user = await create_user(company, email="blocked@example.com")
    refresh_token = "valid-refresh-token-for-revoke-test"
    session_record = AuthSessionModel(
        user_id=user.id,
        tenant_id=user.tenant_id,
        refresh_token_hash=TokenService().hash_refresh_token(refresh_token),
        expires_at=datetime.now(UTC).replace(year=datetime.now(UTC).year + 1),
    )
    async with async_session_factory() as session:
        session.add(session_record)
        await session.commit()

    response = await users_client.post(f"/api/v1/users/{user.id}/block", headers=auth_header(admin))
    assert response.status_code == 200
    assert response.json()["status"] == "blocked"

    login = await users_client.post(
        "/api/v1/auth/login",
        json={"email": "blocked@example.com", "password": "Senha123"},
    )
    refresh = await users_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})

    assert login.status_code == 403
    assert refresh.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_failed_login_attempts_are_tracked_and_reset(users_client: AsyncClient) -> None:
    company = await create_company(slug="login-company", code="LOGIN", document_seed=7)
    user = await create_user(company, email="login@example.com")

    failed = await users_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "errada123"},
    )
    assert failed.status_code == 401

    async with async_session_factory() as session:
        db_user = await session.get(AuthUserModel, user.id)
        assert db_user is not None
        assert db_user.failed_login_attempts == 1

    success = await users_client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "Senha123"},
    )
    assert success.status_code == 200

    async with async_session_factory() as session:
        result = await session.execute(select(AuthUserModel).where(AuthUserModel.id == user.id))
        db_user = result.scalar_one()
        assert db_user.failed_login_attempts == 0
        assert db_user.last_login_at is not None
