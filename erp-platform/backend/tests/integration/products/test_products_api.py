from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.audit.infrastructure.models import AuditEventModel
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel
from app.modules.products.infrastructure.models import ProductModel


@pytest_asyncio.fixture
async def products_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest_asyncio.fixture(autouse=True)
async def clean_tables() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(AuditEventModel))
        await session.execute(delete(ProductModel))
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()
    yield
    async with async_session_factory() as session:
        await session.execute(delete(AuditEventModel))
        await session.execute(delete(ProductModel))
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


async def create_company(*, slug: str, code: str, document_seed: int) -> CompanyModel:
    company = CompanyModel(
        id=uuid4(),
        legal_name=f"{slug} Ltda",
        trade_name=slug,
        document=valid_cnpj(document_seed),
        email=f"contato@{slug}.com.br",
        phone="75982165869",
        slug=slug,
        code=code,
        status=CompanyStatus.ACTIVE,
        timezone="America/Sao_Paulo",
        locale="pt-BR",
        currency="BRL",
        is_active=True,
    )
    async with async_session_factory() as session:
        session.add(company)
        await session.commit()
        await session.refresh(company)
    return company


async def create_user(company: CompanyModel, *, email: str) -> AuthUserModel:
    user = AuthUserModel(
        tenant_id=company.id,
        tenant_slug=company.slug,
        email=email.lower(),
        password_hash=PasswordService().hash("Senha123"),
        is_active=True,
        is_superuser=False,
    )
    async with async_session_factory() as session:
        session.add(user)
        await session.commit()
        await session.refresh(user)
    return user


def auth_header(user: AuthUserModel) -> dict[str, str]:
    token = TokenService().create_access_token(user.id, user.tenant_id)
    return {"Authorization": f"Bearer {token}", "X-Correlation-ID": "products-test"}


def product_payload(
    *,
    internal_code: str = "PRD-001",
    barcode: str | None = "789100000001",
    name: str = "Hamburguer Artesanal",
) -> dict:
    return {
        "name": name,
        "description": "Produto para venda no restaurante.",
        "internal_code": internal_code,
        "barcode": barcode,
        "product_type": "prepared_item",
        "unit_of_measure": "unit",
        "sale_price": "29.90",
        "cost_price": "12.40",
        "main_image_url": "https://example.com/images/product.png",
        "is_available_for_sale": True,
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_can_manage_products_in_own_tenant(products_client: AsyncClient) -> None:
    company = await create_company(slug="restaurant-one", code="REST1", document_seed=1)
    user = await create_user(company, email="manager@example.com")
    headers = auth_header(user)

    created = await products_client.post(
        "/api/v1/products",
        json=product_payload(),
        headers=headers,
    )
    assert created.status_code == 201
    body = created.json()
    product_id = body["id"]
    assert body["tenant_id"] == str(company.id)
    assert body["internal_code"] == "PRD-001"
    assert body["sale_price"] == "29.90"
    assert body["request_id"] is not None

    listed = await products_client.get(
        "/api/v1/products",
        params={"search": "hamburguer", "page": 1, "page_size": 10},
        headers=headers,
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1

    updated = await products_client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Hamburguer Especial", "sale_price": "31.50"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Hamburguer Especial"
    assert updated.json()["sale_price"] == "31.50"

    unavailable = await products_client.post(
        f"/api/v1/products/{product_id}/availability",
        json={"is_available_for_sale": False},
        headers=headers,
    )
    assert unavailable.status_code == 200
    assert unavailable.json()["is_available_for_sale"] is False

    deactivated = await products_client.post(
        f"/api/v1/products/{product_id}/deactivate",
        headers=headers,
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["status"] == "inactive"
    assert deactivated.json()["is_active"] is False
    assert deactivated.json()["is_available_for_sale"] is False

    unavailable_inactive = await products_client.post(
        f"/api/v1/products/{product_id}/availability",
        json={"is_available_for_sale": True},
        headers=headers,
    )
    assert unavailable_inactive.status_code == 409
    assert unavailable_inactive.json()["code"] == "PRODUCT_NOT_AVAILABLE"

    activated = await products_client.post(
        f"/api/v1/products/{product_id}/activate",
        headers=headers,
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"
    assert activated.json()["is_active"] is True
    assert activated.json()["is_available_for_sale"] is False

    deleted = await products_client.delete(f"/api/v1/products/{product_id}", headers=headers)
    assert deleted.status_code == 200

    missing_after_delete = await products_client.get(
        f"/api/v1/products/{product_id}", headers=headers
    )
    assert missing_after_delete.status_code == 404

    async with async_session_factory() as session:
        events = (
            (
                await session.execute(
                    select(AuditEventModel.event_name).where(
                        AuditEventModel.entity_id == product_id
                    )
                )
            )
            .scalars()
            .all()
        )
    assert "product.created" in events
    assert "product.updated" in events
    assert "product.availability.changed" in events
    assert "product.deleted" in events


@pytest.mark.integration
@pytest.mark.asyncio
async def test_product_uniqueness_is_scoped_by_tenant(products_client: AsyncClient) -> None:
    company_one = await create_company(slug="tenant-one", code="TEN1", document_seed=2)
    company_two = await create_company(slug="tenant-two", code="TEN2", document_seed=3)
    user_one = await create_user(company_one, email="one@example.com")
    user_two = await create_user(company_two, email="two@example.com")

    first = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="SKU-001", barcode="BAR-001"),
        headers=auth_header(user_one),
    )
    duplicate_same_tenant = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="SKU-001", barcode="BAR-002"),
        headers=auth_header(user_one),
    )
    same_code_other_tenant = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="SKU-001", barcode="BAR-001"),
        headers=auth_header(user_two),
    )

    assert first.status_code == 201
    assert duplicate_same_tenant.status_code == 409
    assert duplicate_same_tenant.json()["code"] == "PRODUCT_INTERNAL_CODE_ALREADY_EXISTS"
    assert same_code_other_tenant.status_code == 201


@pytest.mark.integration
@pytest.mark.asyncio
async def test_barcode_null_is_allowed_and_duplicate_barcode_is_rejected(
    products_client: AsyncClient,
) -> None:
    company = await create_company(slug="barcode-company", code="BAR", document_seed=4)
    user = await create_user(company, email="barcode@example.com")
    headers = auth_header(user)

    null_one = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="NULL-1", barcode=None),
        headers=headers,
    )
    null_two = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="NULL-2", barcode=None),
        headers=headers,
    )
    duplicate_barcode = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="BAR-2", barcode="BAR-001"),
        headers=headers,
    )
    duplicate_barcode_again = await products_client.post(
        "/api/v1/products",
        json=product_payload(internal_code="BAR-3", barcode="BAR-001"),
        headers=headers,
    )

    assert null_one.status_code == 201
    assert null_two.status_code == 201
    assert duplicate_barcode.status_code == 201
    assert duplicate_barcode_again.status_code == 409
    assert duplicate_barcode_again.json()["code"] == "PRODUCT_BARCODE_ALREADY_EXISTS"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_product_from_another_tenant_is_not_found(products_client: AsyncClient) -> None:
    company_one = await create_company(slug="tenant-a", code="TENA", document_seed=5)
    company_two = await create_company(slug="tenant-b", code="TENB", document_seed=6)
    user_one = await create_user(company_one, email="a@example.com")
    user_two = await create_user(company_two, email="b@example.com")

    created = await products_client.post(
        "/api/v1/products",
        json=product_payload(),
        headers=auth_header(user_one),
    )
    product_id = created.json()["id"]

    response = await products_client.get(
        f"/api/v1/products/{product_id}", headers=auth_header(user_two)
    )
    assert response.status_code == 404


@pytest.mark.integration
@pytest.mark.asyncio
async def test_negative_values_are_rejected(products_client: AsyncClient) -> None:
    company = await create_company(slug="negative-company", code="NEG", document_seed=7)
    user = await create_user(company, email="negative@example.com")

    response = await products_client.post(
        "/api/v1/products",
        json={**product_payload(), "sale_price": "-1.00"},
        headers=auth_header(user),
    )

    assert response.status_code == 400
    assert response.json()["code"] == "PRODUCT_INVALID_PRICE"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_money_boundaries_are_accepted(products_client: AsyncClient) -> None:
    company = await create_company(slug="money-company", code="MONEY", document_seed=8)
    user = await create_user(company, email="money@example.com")
    headers = auth_header(user)

    zero = await products_client.post(
        "/api/v1/products",
        json={**product_payload(internal_code="MONEY-0", barcode=None), "sale_price": "0.00"},
        headers=headers,
    )
    cent = await products_client.post(
        "/api/v1/products",
        json={**product_payload(internal_code="MONEY-1", barcode=None), "sale_price": "0.01"},
        headers=headers,
    )
    limit = await products_client.post(
        "/api/v1/products",
        json={
            **product_payload(internal_code="MONEY-2", barcode=None),
            "sale_price": "9999999999.99",
        },
        headers=headers,
    )
    rounded = await products_client.post(
        "/api/v1/products",
        json={**product_payload(internal_code="MONEY-3", barcode=None), "sale_price": "10.129"},
        headers=headers,
    )

    assert zero.status_code == 201
    assert zero.json()["sale_price"] == "0.00"
    assert cent.status_code == 201
    assert cent.json()["sale_price"] == "0.01"
    assert limit.status_code == 201
    assert limit.json()["sale_price"] == "9999999999.99"
    assert rounded.status_code == 201
    assert rounded.json()["sale_price"] == "10.13"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_deleted_product_cannot_be_updated_activated_or_made_available(
    products_client: AsyncClient,
) -> None:
    company = await create_company(slug="deleted-company", code="DEL", document_seed=9)
    user = await create_user(company, email="deleted@example.com")
    headers = auth_header(user)

    created = await products_client.post(
        "/api/v1/products",
        json=product_payload(),
        headers=headers,
    )
    product_id = created.json()["id"]
    deleted = await products_client.delete(f"/api/v1/products/{product_id}", headers=headers)

    update = await products_client.patch(
        f"/api/v1/products/{product_id}",
        json={"name": "Produto excluído"},
        headers=headers,
    )
    activate = await products_client.post(
        f"/api/v1/products/{product_id}/activate",
        headers=headers,
    )
    availability = await products_client.post(
        f"/api/v1/products/{product_id}/availability",
        json={"is_available_for_sale": True},
        headers=headers,
    )

    assert deleted.status_code == 200
    assert update.status_code == 404
    assert activate.status_code == 404
    assert availability.status_code == 404
