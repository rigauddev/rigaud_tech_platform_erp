from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.audit.infrastructure.models import AuditEventModel
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


@pytest_asyncio.fixture
async def audit_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_tables() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(AuditEventModel))
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()
    yield


def valid_cnpj(seed: int) -> str:
    base = f"{seed:08d}0001"[-12:]

    def digit(value: str, weights: list[int]) -> str:
        total = sum(int(item) * weight for item, weight in zip(value, weights, strict=True))
        remainder = total % 11
        return str(0 if remainder < 2 else 11 - remainder)

    first = digit(base, [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = digit(base + first, [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return base + first + second


async def create_company_and_user(*, is_superuser: bool) -> AuthUserModel:
    company = CompanyModel(
        id=uuid4(),
        legal_name="Audit Ltda",
        trade_name="Audit",
        document=valid_cnpj(90),
        email="audit@example.com",
        phone="75982165869",
        slug=f"audit-{uuid4().hex[:8]}",
        code=f"AUD{uuid4().hex[:6]}".upper(),
        status=CompanyStatus.ACTIVE,
        timezone="America/Sao_Paulo",
        locale="pt-BR",
        currency="BRL",
        is_active=True,
    )
    user = AuthUserModel(
        tenant_id=company.id,
        tenant_slug=company.slug,
        email=f"user-{uuid4().hex[:8]}@example.com",
        password_hash=PasswordService().hash("Senha123"),
        is_active=True,
        is_superuser=is_superuser,
    )
    async with async_session_factory() as session:
        session.add(company)
        await session.flush()
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


def auth_header(user: AuthUserModel) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {TokenService().create_access_token(user.id, user.tenant_id)}"
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_and_correlation_headers(audit_client: AsyncClient) -> None:
    response = await audit_client.get("/api/v1/health", headers={"X-Correlation-ID": "support-123"})
    assert response.headers["x-request-id"]
    assert response.headers["x-correlation-id"] == "support-123"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_correlation_id_is_rejected(audit_client: AsyncClient) -> None:
    response = await audit_client.get("/api/v1/health", headers={"X-Correlation-ID": "bad value"})
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_superuser_can_list_audit_events(audit_client: AsyncClient) -> None:
    admin = await create_company_and_user(is_superuser=True)
    event = AuditEventModel(
        event_name="company.created",
        module="companies",
        action="created",
        tenant_id=admin.tenant_id,
        actor_user_id=admin.id,
    )
    async with async_session_factory() as session:
        session.add(event)
        await session.commit()
        await session.refresh(event)

    listed = await audit_client.get("/api/v1/audit/events", headers=auth_header(admin))
    detail = await audit_client.get(f"/api/v1/audit/events/{event.id}", headers=auth_header(admin))

    assert listed.status_code == 200
    assert listed.json()["success"] is True
    assert listed.json()["items"][0]["event_name"] == "company.created"
    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == str(event.id)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_common_user_cannot_list_audit_events(audit_client: AsyncClient) -> None:
    user = await create_company_and_user(is_superuser=False)
    response = await audit_client.get("/api/v1/audit/events", headers=auth_header(user))
    assert response.status_code == 403
