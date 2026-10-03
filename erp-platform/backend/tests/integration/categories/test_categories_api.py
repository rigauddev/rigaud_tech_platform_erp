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
from app.modules.categories.infrastructure.models import CategoryModel
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.infrastructure.models import CompanyModel


@pytest_asyncio.fixture
async def categories_client() -> AsyncClient:
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
        await session.execute(delete(CategoryModel))
        await session.execute(delete(AuthSessionModel))
        await session.execute(delete(AuthUserModel))
        await session.execute(delete(CompanyModel))
        await session.commit()
    yield
    async with async_session_factory() as session:
        await session.execute(delete(AuditEventModel))
        await session.execute(delete(CategoryModel))
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
    return {"Authorization": f"Bearer {token}", "X-Correlation-ID": "categories-test"}


def category_payload(
    *,
    internal_code: str = "CAT-001",
    name: str = "Bebidas",
    parent_id: str | None = None,
    slug: str | None = None,
    display_order: int = 0,
) -> dict:
    return {
        "name": name,
        "internal_code": internal_code,
        "parent_id": parent_id,
        "slug": slug,
        "description": "Categoria operacional compartilhada.",
        "icon": "restaurant_menu",
        "color": "#0088AA",
        "display_order": display_order,
    }


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_can_manage_category_hierarchy(categories_client: AsyncClient) -> None:
    company = await create_company(slug="category-restaurant", code="CATREST", document_seed=21)
    user = await create_user(company, email="manager@example.com")
    headers = auth_header(user)

    root = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(),
        headers=headers,
    )
    assert root.status_code == 201
    root_id = root.json()["id"]
    assert root.json()["slug"] == "bebidas"
    assert root.json()["tenant_id"] == str(company.id)

    child = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(
            internal_code="CAT-002",
            name="Refrigerantes",
            parent_id=root_id,
            display_order=1,
        ),
        headers=headers,
    )
    assert child.status_code == 201
    child_id = child.json()["id"]

    listed = await categories_client.get(
        "/api/v1/categories",
        params={"tree": True, "ordering": "manual"},
        headers=headers,
    )
    assert listed.status_code == 200
    tree = listed.json()["data"]
    assert tree[0]["name"] == "Bebidas"
    assert tree[0]["children"][0]["name"] == "Refrigerantes"

    cycle = await categories_client.patch(
        f"/api/v1/categories/{root_id}",
        json={"parent_id": child_id},
        headers=headers,
    )
    assert cycle.status_code == 409
    assert cycle.json()["code"] == "CATEGORY_CYCLE_DETECTED"

    moved_to_root = await categories_client.patch(
        f"/api/v1/categories/{child_id}",
        json={"parent_id": None},
        headers=headers,
    )
    assert moved_to_root.status_code == 200
    assert moved_to_root.json()["parent_id"] is None

    moved_back = await categories_client.patch(
        f"/api/v1/categories/{child_id}",
        json={"parent_id": root_id},
        headers=headers,
    )
    assert moved_back.status_code == 200
    assert moved_back.json()["parent_id"] == root_id

    reordered = await categories_client.post(
        f"/api/v1/categories/{child_id}/reorder",
        json={"display_order": 7},
        headers=headers,
    )
    assert reordered.status_code == 200
    assert reordered.json()["display_order"] == 7

    deactivated = await categories_client.post(
        f"/api/v1/categories/{child_id}/deactivate",
        headers=headers,
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["status"] == "inactive"

    activated = await categories_client.post(
        f"/api/v1/categories/{child_id}/activate",
        headers=headers,
    )
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"

    blocked_delete = await categories_client.delete(
        f"/api/v1/categories/{root_id}", headers=headers
    )
    assert blocked_delete.status_code == 409
    assert blocked_delete.json()["code"] == "CATEGORY_IN_USE"

    deleted_child = await categories_client.delete(
        f"/api/v1/categories/{child_id}",
        headers=headers,
    )
    assert deleted_child.status_code == 200

    missing_after_delete = await categories_client.get(
        f"/api/v1/categories/{child_id}",
        headers=headers,
    )
    assert missing_after_delete.status_code == 404

    async with async_session_factory() as session:
        events = (
            (
                await session.execute(
                    select(AuditEventModel.event_name).where(
                        AuditEventModel.entity_id.in_([root_id, child_id])
                    )
                )
            )
            .scalars()
            .all()
        )
    assert "category.created" in events
    assert "category.reordered" in events
    assert "category.deleted" in events


@pytest.mark.integration
@pytest.mark.asyncio
async def test_category_uniqueness_is_scoped_by_tenant(categories_client: AsyncClient) -> None:
    company_one = await create_company(slug="cat-tenant-one", code="CT1", document_seed=22)
    company_two = await create_company(slug="cat-tenant-two", code="CT2", document_seed=23)
    user_one = await create_user(company_one, email="one@example.com")
    user_two = await create_user(company_two, email="two@example.com")

    first = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(internal_code="MENU-001", name="Bebidas"),
        headers=auth_header(user_one),
    )
    duplicate_code = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(internal_code="MENU-001", name="Pratos", slug="pratos"),
        headers=auth_header(user_one),
    )
    duplicate_slug = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(internal_code="MENU-002", name="Bebidas"),
        headers=auth_header(user_one),
    )
    same_other_tenant = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(internal_code="MENU-001", name="Bebidas"),
        headers=auth_header(user_two),
    )

    assert first.status_code == 201
    assert duplicate_code.status_code == 409
    assert duplicate_code.json()["code"] == "CATEGORY_INTERNAL_CODE_ALREADY_EXISTS"
    assert duplicate_slug.status_code == 409
    assert duplicate_slug.json()["code"] == "CATEGORY_SLUG_ALREADY_EXISTS"
    assert same_other_tenant.status_code == 201


@pytest.mark.integration
@pytest.mark.asyncio
async def test_category_from_another_tenant_is_not_found(categories_client: AsyncClient) -> None:
    company_one = await create_company(slug="cat-a", code="CATA", document_seed=24)
    company_two = await create_company(slug="cat-b", code="CATB", document_seed=25)
    user_one = await create_user(company_one, email="a@example.com")
    user_two = await create_user(company_two, email="b@example.com")

    created = await categories_client.post(
        "/api/v1/categories",
        json=category_payload(),
        headers=auth_header(user_one),
    )
    category_id = created.json()["id"]

    response = await categories_client.get(
        f"/api/v1/categories/{category_id}",
        headers=auth_header(user_two),
    )

    assert response.status_code == 404
