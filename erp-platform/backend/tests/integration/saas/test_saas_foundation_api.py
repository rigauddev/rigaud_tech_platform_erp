from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete

from app.database.session import async_session_factory
from app.main import create_app
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.infrastructure.models import AuthSessionModel, AuthUserModel
from app.modules.billing.infrastructure.models import BillingEventModel
from app.modules.companies.infrastructure.models import (
    BranchMembershipModel,
    BranchModel,
    CompanyMembershipModel,
    CompanyModel,
)
from app.modules.entitlements.infrastructure.models import TenantEntitlementModel
from app.modules.feature_flags.infrastructure.models import FeatureFlagModel
from app.modules.plan.infrastructure.models import PlanEntitlementModel, PlanLimitModel, PlanModel
from app.modules.subscription.infrastructure.models import SubscriptionModel


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
        for model in (
            BillingEventModel,
            TenantEntitlementModel,
            FeatureFlagModel,
            SubscriptionModel,
            PlanLimitModel,
            PlanEntitlementModel,
            PlanModel,
            AuthSessionModel,
            BranchMembershipModel,
            CompanyMembershipModel,
            BranchModel,
            AuthUserModel,
            CompanyModel,
        ):
            await session.execute(delete(model))
        await session.commit()
    yield
    async with async_session_factory() as session:
        for model in (
            BillingEventModel,
            TenantEntitlementModel,
            FeatureFlagModel,
            SubscriptionModel,
            PlanLimitModel,
            PlanEntitlementModel,
            PlanModel,
            AuthSessionModel,
            BranchMembershipModel,
            CompanyMembershipModel,
            BranchModel,
            AuthUserModel,
            CompanyModel,
        ):
            await session.execute(delete(model))
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
        document=valid_cnpj(90),
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


def starter_plan_payload() -> dict:
    return {
        "code": "starter",
        "name": "Starter",
        "description": "Plano inicial",
        "monthly_price": "99.90",
        "annual_price": "999.00",
        "trial_days": 14,
        "is_trial_available": True,
        "is_active": True,
        "display_order": 1,
        "entitlements": [
            {"entitlement_key": "products", "entitlement_type": "module", "is_enabled": True},
            {"entitlement_key": "delivery", "entitlement_type": "feature", "is_enabled": False},
            {"entitlement_key": "web", "entitlement_type": "feature", "is_enabled": True},
        ],
        "limits": [
            {"limit_key": "users", "limit_value": 5},
            {"limit_key": "branches", "limit_value": 1},
            {"limit_key": "products", "limit_value": 5000},
        ],
    }


def professional_plan_payload() -> dict:
    payload = starter_plan_payload()
    payload.update(
        {
            "code": "professional",
            "name": "Professional",
            "monthly_price": "199.90",
            "annual_price": "1999.00",
            "display_order": 2,
            "entitlements": [
                {"entitlement_key": "products", "entitlement_type": "module", "is_enabled": True},
                {"entitlement_key": "delivery", "entitlement_type": "feature", "is_enabled": True},
                {"entitlement_key": "kds", "entitlement_type": "feature", "is_enabled": True},
            ],
        }
    )
    return payload


@pytest.mark.integration
@pytest.mark.asyncio
async def test_saas_foundation_flow(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "SaaS Tenant Ltda",
            "trade_name": "SaaS Tenant",
            "document": valid_cnpj(91),
            "slug": "saas-tenant",
            "code": "SAAST",
        },
    )
    tenant_id = company_response.json()["id"]

    starter_response = await client.post(
        "/api/v1/plans", headers=headers, json=starter_plan_payload()
    )
    assert starter_response.status_code == 201
    starter_id = starter_response.json()["id"]

    professional_response = await client.post(
        "/api/v1/plans", headers=headers, json=professional_plan_payload()
    )
    assert professional_response.status_code == 201
    professional_id = professional_response.json()["id"]

    subscription_response = await client.post(
        "/api/v1/subscriptions",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "plan_id": starter_id,
            "status": "trial",
            "billing_provider": "fake",
            "grace_period_days": 7,
        },
    )
    assert subscription_response.status_code == 200
    subscription = subscription_response.json()
    assert subscription["status"] == "trial"
    assert subscription["external_reference"].startswith("fake_")

    await client.post(
        "/api/v1/users",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "email": "owner@saas.test",
            "password": "Senha123",
            "must_change_password": False,
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"tenant": "saas-tenant", "email": "owner@saas.test", "password": "Senha123"},
    )
    user_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

    current_subscription = await client.get("/api/v1/subscriptions/current", headers=user_headers)
    assert current_subscription.status_code == 200
    assert current_subscription.json()["id"] == subscription["id"]

    entitlements = await client.get("/api/v1/entitlements", headers=user_headers)
    assert entitlements.status_code == 200
    assert {item["entitlement_key"] for item in entitlements.json()["items"]} >= {
        "products",
        "delivery",
        "web",
    }

    delivery_check = await client.get("/api/v1/entitlements/delivery", headers=user_headers)
    assert delivery_check.status_code == 200
    assert delivery_check.json()["is_enabled"] is False

    upgrade_response = await client.post(
        f"/api/v1/subscriptions/{subscription['id']}/change-plan",
        headers=headers,
        json={"plan_id": professional_id},
    )
    assert upgrade_response.status_code == 200
    assert upgrade_response.json()["plan_id"] == professional_id

    delivery_after_upgrade = await client.get("/api/v1/entitlements/delivery", headers=user_headers)
    assert delivery_after_upgrade.json()["is_enabled"] is True

    past_due = await client.post(
        f"/api/v1/subscriptions/{subscription['id']}/billing-status",
        headers=headers,
        json={"status": "past_due"},
    )
    assert past_due.status_code == 200
    assert past_due.json()["grace_period_ends_at"] is not None

    suspended = await client.post(
        f"/api/v1/subscriptions/{subscription['id']}/billing-status",
        headers=headers,
        json={"status": "suspended"},
    )
    assert suspended.status_code == 200
    assert suspended.json()["status"] == "suspended"

    feature_flag = await client.post(
        "/api/v1/feature-flags",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "feature_key": "qr_menu",
            "name": "QR Menu",
            "scope": "tenant",
            "is_enabled": True,
        },
    )
    assert feature_flag.status_code == 200
    assert feature_flag.json()["is_enabled"] is True

    disabled_feature = await client.patch(
        f"/api/v1/feature-flags/{feature_flag.json()['id']}",
        headers=headers,
        json={"is_enabled": False},
    )
    assert disabled_feature.status_code == 200
    assert disabled_feature.json()["is_enabled"] is False

    billing_event = await client.post(
        "/api/v1/billing/events/fake",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "subscription_id": subscription["id"],
            "event_type": "payment_confirmed",
            "external_event_id": "evt_fake_1",
            "payload": {"amount": "199.90"},
        },
    )
    assert billing_event.status_code == 200
    assert billing_event.json()["event_type"] == "payment_confirmed"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_inactive_plan_cannot_start_subscription(client: AsyncClient) -> None:
    admin = await create_platform_admin()
    headers = auth_header(admin)

    company_response = await client.post(
        "/api/v1/companies",
        headers=headers,
        json={
            "legal_name": "Inactive Plan Tenant Ltda",
            "trade_name": "Inactive Plan Tenant",
            "document": valid_cnpj(92),
            "slug": "inactive-plan-tenant",
            "code": "INACTP",
        },
    )
    tenant_id = company_response.json()["id"]
    payload = starter_plan_payload()
    payload["code"] = "inactive"
    payload["is_active"] = False
    plan_response = await client.post("/api/v1/plans", headers=headers, json=payload)

    subscription_response = await client.post(
        "/api/v1/subscriptions",
        headers=headers,
        json={
            "tenant_id": tenant_id,
            "plan_id": plan_response.json()["id"],
            "status": "active",
        },
    )

    assert subscription_response.status_code == 409
    assert subscription_response.json()["code"] == "PLAN_INACTIVE"
