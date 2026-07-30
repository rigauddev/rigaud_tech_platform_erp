from dataclasses import dataclass
from uuid import UUID, uuid4

from app.modules.billing.domain.entities import BillingProviderCode


@dataclass(frozen=True)
class BillingProviderResult:
    provider: BillingProviderCode
    external_reference: str
    status: str


class BillingProvider:
    code: BillingProviderCode

    async def create_subscription(self, tenant_id: UUID, plan_id: UUID) -> BillingProviderResult:
        raise NotImplementedError


class FakeBillingProvider(BillingProvider):
    code = BillingProviderCode.FAKE

    async def create_subscription(self, tenant_id: UUID, plan_id: UUID) -> BillingProviderResult:
        return BillingProviderResult(
            provider=self.code,
            external_reference=f"fake_{tenant_id}_{plan_id}_{uuid4().hex[:8]}",
            status="created",
        )
