from uuid import UUID, uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


@pytest_asyncio.fixture
async def companies_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
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
    slug: str = "admin-company",
    code: str = "ADMIN",
    document_seed: int = 1,
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


async def create_user(company: CompanyModel, *, is_superuser: bool) -> AuthUserModel:
    user = AuthUserModel(
        tenant_id=company.id,
        tenant_slug=company.slug,
        email=f"user-{company.slug}@example.com",
        password_hash=PasswordService().hash("Senha123"),
        is_active=True,
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


def create_payload(
    *,
    document: str = "11222333000181",
    slug: str = "rigaud-tech",
    code: str = "RIGAUD",
) -> dict[str, str]:
    return {
        "legal_name": "Rigaud Tecnologia Ltda",
        "trade_name": "Rigaud Tech",
        "document": document,
        "email": "contato@empresa.com.br",
        "phone": "75982165869",
        "slug": slug,
        "code": code,
        "timezone": "America/Sao_Paulo",
        "locale": "pt-BR",
        "currency": "BRL",
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_superuser_can_create_list_update_and_change_company_status(
    companies_client: AsyncClient,
) -> None:
    admin_company = await create_company()
    admin = await create_user(admin_company, is_superuser=True)

    created = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(),
        headers=auth_header(admin),
    )
    assert created.status_code == 201
    company_id = created.json()["id"]
    assert created.json()["document"] == "11222333000181"

    listed = await companies_client.get("/api/v1/companies", headers=auth_header(admin))
    assert listed.status_code == 200
    assert listed.json()["total"] == 2

    current = await companies_client.get("/api/v1/companies/current", headers=auth_header(admin))
    assert current.status_code == 200
    assert current.json()["id"] == str(admin_company.id)

    updated = await companies_client.patch(
        f"/api/v1/companies/{company_id}",
        json={"trade_name": "Rigaud ERP", "code": "RIGAUDERP"},
        headers=auth_header(admin),
    )
    assert updated.status_code == 200
    assert updated.json()["trade_name"] == "Rigaud ERP"
    assert updated.json()["code"] == "RIGAUDERP"

    deactivated = await companies_client.post(
        f"/api/v1/companies/{company_id}/deactivate",
        headers=auth_header(admin),
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["status"] == "inactive"
    assert deactivated.json()["is_active"] is False

    activated = await companies_client.post(
        f"/api/v1/companies/{company_id}/activate",
        headers=auth_header(admin),
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    suspended = await companies_client.post(
        f"/api/v1/companies/{company_id}/suspend",
        headers=auth_header(admin),
    )
    assert suspended.status_code == 200
    assert suspended.json()["status"] == "suspended"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_company_uniqueness_is_controlled(companies_client: AsyncClient) -> None:
    admin_company = await create_company()
    admin = await create_user(admin_company, is_superuser=True)
    headers = auth_header(admin)

    first = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(),
        headers=headers,
    )
    assert first.status_code == 201

    duplicate_document = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(slug="other-slug", code="OTHER"),
        headers=headers,
    )
    duplicate_slug = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(document=valid_cnpj(2), code="OTHER2"),
        headers=headers,
    )
    duplicate_code = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(document=valid_cnpj(3), slug="other-slug-2"),
        headers=headers,
    )

    assert duplicate_document.status_code == 409
    assert duplicate_slug.status_code == 409
    assert duplicate_code.status_code == 409


@pytest.mark.integration
@pytest.mark.asyncio
async def test_common_user_cannot_administer_companies_but_can_read_current(
    companies_client: AsyncClient,
) -> None:
    company = await create_company()
    user = await create_user(company, is_superuser=False)
    headers = auth_header(user)

    listed = await companies_client.get("/api/v1/companies", headers=headers)
    created = await companies_client.post(
        "/api/v1/companies",
        json=create_payload(document=valid_cnpj(10), slug="blocked", code="BLOCKED"),
        headers=headers,
    )
    current = await companies_client.get("/api/v1/companies/current", headers=headers)
    own = await companies_client.get(f"/api/v1/companies/{company.id}", headers=headers)
    other_company_id = UUID("11111111-1111-4111-8111-111111111111")
    other = await companies_client.get(f"/api/v1/companies/{other_company_id}", headers=headers)

    assert listed.status_code == 403
    assert created.status_code == 403
    assert current.status_code == 200
    assert own.status_code == 200
    assert other.status_code == 403
