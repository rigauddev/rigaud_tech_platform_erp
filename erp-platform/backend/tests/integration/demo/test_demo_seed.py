import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, func, select

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.infrastructure.models import (
    AuthSessionModel,
    AuthUserModel,
    MfaRecoveryCodeModel,
    UserMfaMethodModel,
)
from app.modules.categories.infrastructure.models import CategoryModel
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
    WarehouseModel,
)
from app.modules.products.infrastructure.models import ProductModel
from app.security.passwords import verify_password
from app.shared.demo.data import PLATFORM_SLUG, RESTAURANT_SLUG, RETAIL_SLUG
from app.shared.demo.service import DemoSeeder


@pytest_asyncio.fixture(autouse=True)
async def clean_demo_tables() -> None:
    async with async_session_factory() as session:
        await _clean(session)
        await session.commit()
    yield
    async with async_session_factory() as session:
        await _clean(session)
        await session.commit()


async def _clean(session) -> None:
    await session.execute(delete(AuthSessionModel))
    await session.execute(delete(UserMfaMethodModel))
    await session.execute(delete(MfaRecoveryCodeModel))
    await session.execute(delete(BranchMembershipModel))
    await session.execute(delete(CompanyMembershipModel))
    await session.execute(delete(InventoryReservationModel))
    await session.execute(delete(InventoryAdjustmentModel))
    await session.execute(delete(InventoryMovementModel))
    await session.execute(delete(InventoryBalanceModel))
    await session.execute(delete(WarehouseModel))
    await session.execute(delete(ProductModel))
    await session.execute(delete(CategoryModel))
    await session.execute(delete(BranchModel))
    await session.execute(delete(AuthUserModel))
    await session.execute(delete(CompanyModel))


async def count_rows(model) -> int:
    async with async_session_factory() as session:
        return (await session.execute(select(func.count()).select_from(model))).scalar_one()


@pytest_asyncio.fixture
async def demo_client() -> AsyncClient:
    app = create_app()
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        yield client


@pytest.mark.integration
@pytest.mark.asyncio
async def test_demo_seed_all_is_idempotent() -> None:
    async with async_session_factory() as session:
        first = await DemoSeeder(session).seed_all()

    assert first.as_dict() == {
        "mode": "all",
        "companies": 3,
        "branches": 5,
        "users": 18,
        "memberships": 18,
        "branch_memberships": 37,
        "warehouses": 10,
        "categories": 9,
        "products": 130,
        "deleted_rows": 0,
    }

    counts_after_first = {
        "companies": await count_rows(CompanyModel),
        "branches": await count_rows(BranchModel),
        "users": await count_rows(AuthUserModel),
        "memberships": await count_rows(CompanyMembershipModel),
        "branch_memberships": await count_rows(BranchMembershipModel),
        "warehouses": await count_rows(WarehouseModel),
        "categories": await count_rows(CategoryModel),
        "products": await count_rows(ProductModel),
    }

    async with async_session_factory() as session:
        await DemoSeeder(session).seed_all()

    counts_after_second = {
        "companies": await count_rows(CompanyModel),
        "branches": await count_rows(BranchModel),
        "users": await count_rows(AuthUserModel),
        "memberships": await count_rows(CompanyMembershipModel),
        "branch_memberships": await count_rows(BranchMembershipModel),
        "warehouses": await count_rows(WarehouseModel),
        "categories": await count_rows(CategoryModel),
        "products": await count_rows(ProductModel),
    }
    assert counts_after_second == counts_after_first

    async with async_session_factory() as session:
        admin = (
            await session.execute(
                select(AuthUserModel).where(AuthUserModel.email == "admin@demo.local")
            )
        ).scalar_one()
    assert verify_password("123456", admin.password_hash)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_demo_reset_preserves_platform_tenant() -> None:
    async with async_session_factory() as session:
        await DemoSeeder(session).seed_all()
        summary = await DemoSeeder(session).reset()

    assert summary.deleted_rows > 0

    async with async_session_factory() as session:
        slugs = (
            (await session.execute(select(CompanyModel.slug).order_by(CompanyModel.slug)))
            .scalars()
            .all()
        )
    assert slugs == [PLATFORM_SLUG]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_demo_segment_seeds_can_run_independently() -> None:
    async with async_session_factory() as session:
        restaurant = await DemoSeeder(session).seed_restaurant()
        retail = await DemoSeeder(session).seed_retail()

    assert restaurant.products == 50
    assert retail.products == 80
    assert restaurant.warehouses == 6
    assert retail.warehouses == 4

    async with async_session_factory() as session:
        demo_slugs = (
            (
                await session.execute(
                    select(CompanyModel.slug)
                    .where(CompanyModel.slug.in_((RESTAURANT_SLUG, RETAIL_SLUG)))
                    .order_by(CompanyModel.slug)
                )
            )
            .scalars()
            .all()
        )
    assert demo_slugs == [RETAIL_SLUG, RESTAURANT_SLUG]


@pytest.mark.integration
@pytest.mark.asyncio
async def test_demo_api_installs_reports_and_resets(demo_client: AsyncClient) -> None:
    install = await demo_client.get("/api/v1/demo/install")
    assert install.status_code == 200
    assert install.json()["code"] == "DEMO_INSTALLED"
    assert install.json()["warehouses"] == 10
    assert install.json()["products"] == 130

    status = await demo_client.get("/api/v1/demo/status")
    assert status.status_code == 200
    assert status.json()["companies"] == 3
    assert status.json()["warehouses"] == 10
    assert status.json()["scenarios"]["restaurant"] == 4

    scenarios = await demo_client.get("/api/v1/demo/scenarios")
    assert scenarios.status_code == 200
    assert scenarios.json()["data"]["status"] == "planned"

    reset = await demo_client.get("/api/v1/demo/reset")
    assert reset.status_code == 200
    assert reset.json()["code"] == "DEMO_RESET"
