from uuid import UUID

from app.modules.entitlements.infrastructure.models import TenantEntitlementModel
from app.modules.entitlements.infrastructure.repositories import SQLAlchemyEntitlementRepository


class ListTenantEntitlements:
    def __init__(self, entitlements: SQLAlchemyEntitlementRepository) -> None:
        self.entitlements = entitlements

    async def execute(self, tenant_id: UUID) -> list[TenantEntitlementModel]:
        return await self.entitlements.list_by_tenant(tenant_id)


class CheckEntitlement:
    def __init__(self, entitlements: SQLAlchemyEntitlementRepository) -> None:
        self.entitlements = entitlements

    async def execute(self, tenant_id: UUID, entitlement_key: str) -> bool:
        entitlement = await self.entitlements.get(
            tenant_id, entitlement_key.strip().lower().replace("-", "_")
        )
        return bool(entitlement and entitlement.is_enabled)
