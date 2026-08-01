from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


@pytest_asyncio.fixture
async def auth_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_auth_tables() -> None:
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


async def create_auth_user(
    tenant_slug: str = "rigaud-demo",
    tenant_code: str | None = None,
    email: str = "admin@rigaudtech.com.br",
    password: str = "Senha123",
    is_active: bool = True,
    deleted: bool = False,
    company_status: CompanyStatus = CompanyStatus.ACTIVE,
    is_company_active: bool = True,
) -> AuthUserModel:
    async with async_session_factory() as session:
        result = await session.execute(select(CompanyModel).where(CompanyModel.slug == tenant_slug))
        company = result.scalar_one_or_none()
        if company is None:
            company = CompanyModel(
                id=uuid4(),
                legal_name=f"{tenant_slug} Ltda",
                trade_name=tenant_slug,
                document=valid_cnpj(abs(hash(tenant_slug)) % 99_999_999),
                email=f"contato@{tenant_slug}.com.br",
                phone="75982165869",
                slug=tenant_slug,
                code=tenant_code or tenant_slug.replace("-", "_").upper()[:20],
                status=company_status,
                timezone="America/Sao_Paulo",
                locale="pt-BR",
                currency="BRL",
                is_active=is_company_active,
            )
            session.add(company)
            await session.flush()
        user = AuthUserModel(
            tenant_id=company.id,
            tenant_slug=tenant_slug,
            email=email.lower(),
            password_hash=PasswordService().hash(password),
            is_active=is_active,
            is_superuser=False,
            deleted_at=datetime.now(UTC) if deleted else None,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_refresh_logout_and_me(auth_client: AsyncClient) -> None:
    user = await create_auth_user()

    login_response = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": " ADMIN@RIGAUDTECH.COM.BR ",
            "password": "Senha123",
        },
    )

    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"
    assert "refresh_token" in tokens

    me_response = await auth_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["id"] == str(user.id)
    assert "password_hash" not in me_response.text

    refresh_response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()

    reuse_response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert reuse_response.status_code == 401

    logout_response = await auth_client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": rotated_tokens["refresh_token"]},
    )
    assert logout_response.status_code == 200

    logged_out_refresh = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": rotated_tokens["refresh_token"]},
    )
    assert logged_out_refresh.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_login_is_generic(auth_client: AsyncClient) -> None:
    await create_auth_user()

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rigaudtech.com.br", "password": "errada123"},
    )

    assert response.status_code == 401
    assert response.json()["message"] == "Credenciais inválidas."


@pytest.mark.integration
@pytest.mark.asyncio
async def test_login_resolves_tenant_from_user_email(auth_client: AsyncClient) -> None:
    await create_auth_user(tenant_slug="rigaud-demo", tenant_code="RIGAUD")

    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rigaudtech.com.br", "password": "Senha123"},
    )

    assert response.status_code == 200


@pytest.mark.integration
@pytest.mark.asyncio
async def test_inactive_and_suspended_company_blocks_login(auth_client: AsyncClient) -> None:
    await create_auth_user(
        tenant_slug="inactive-company",
        email="inactive-company@example.com",
        company_status=CompanyStatus.INACTIVE,
        is_company_active=False,
    )
    await create_auth_user(
        tenant_slug="suspended-company",
        email="suspended-company@example.com",
        company_status=CompanyStatus.SUSPENDED,
        is_company_active=False,
    )

    inactive = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "inactive-company@example.com",
            "password": "Senha123",
        },
    )
    suspended = await auth_client.post(
        "/api/v1/auth/login",
        json={
            "email": "suspended-company@example.com",
            "password": "Senha123",
        },
    )

    assert inactive.status_code == 403
    assert suspended.status_code == 403


@pytest.mark.integration
@pytest.mark.asyncio
async def test_inactive_and_deleted_users_cannot_login(auth_client: AsyncClient) -> None:
    await create_auth_user(email="inactive@example.com", is_active=False)
    await create_auth_user(email="deleted@example.com", deleted=True)

    inactive = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "password": "Senha123"},
    )
    deleted = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "deleted@example.com", "password": "Senha123"},
    )

    assert inactive.status_code == 403
    assert deleted.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_same_email_cannot_exist_in_different_tenants(auth_client: AsyncClient) -> None:
    await create_auth_user(tenant_slug="tenant-one", email="shared@example.com")

    with pytest.raises(IntegrityError):
        await create_auth_user(tenant_slug="tenant-two", email="shared@example.com")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_same_email_cannot_be_duplicated_in_same_tenant_slug() -> None:
    await create_auth_user(tenant_slug="tenant-one", email="shared@example.com")

    with pytest.raises(IntegrityError):
        await create_auth_user(tenant_slug="tenant-one", email="shared@example.com")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_expired_refresh_token_is_rejected(auth_client: AsyncClient) -> None:
    user = await create_auth_user()
    expired_refresh_token = "expired-refresh-token-with-valid-schema-length"
    session = AuthSessionModel(
        user_id=user.id,
        tenant_id=user.tenant_id,
        refresh_token_hash=TokenService().hash_refresh_token(expired_refresh_token),
        expires_at=datetime.now(UTC) - timedelta(minutes=1),
    )
    async with async_session_factory() as db:
        db.add(session)
        await db.commit()

    response = await auth_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": expired_refresh_token},
    )

    assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
async def test_refresh_hash_is_persisted_without_plain_token(auth_client: AsyncClient) -> None:
    await create_auth_user()
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"email": "admin@rigaudtech.com.br", "password": "Senha123"},
    )
    refresh_token = response.json()["refresh_token"]

    async with async_session_factory() as session:
        result = await session.execute(select(AuthSessionModel))
        auth_session = result.scalar_one()

    assert auth_session.refresh_token_hash != refresh_token
    assert refresh_token not in auth_session.refresh_token_hash
