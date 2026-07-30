from uuid import uuid4

import pytest

from app.modules.billing.application.providers import FakeBillingProvider
from app.modules.billing.domain.entities import BillingProviderCode
from app.modules.subscription.domain.entities import SubscriptionStatus


@pytest.mark.unit
def test_subscription_status_usage_policy() -> None:
    assert SubscriptionStatus.TRIAL.allows_regular_usage is True
    assert SubscriptionStatus.ACTIVE.allows_regular_usage is True
    assert SubscriptionStatus.PAST_DUE.allows_regular_usage is True
    assert SubscriptionStatus.SUSPENDED.allows_regular_usage is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_fake_billing_provider_returns_external_reference() -> None:
    tenant_id = uuid4()
    plan_id = uuid4()

    result = await FakeBillingProvider().create_subscription(tenant_id, plan_id)

    assert result.provider == BillingProviderCode.FAKE
    assert str(tenant_id) in result.external_reference
    assert str(plan_id) in result.external_reference
    assert result.status == "created"
