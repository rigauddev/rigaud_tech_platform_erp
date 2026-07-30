from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.entitlements.infrastructure.models import TenantEntitlementModel


class SQLAlchemyEntitlementRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, entitlement: TenantEntitlementModel) -> TenantEntitlementModel:
        self.session.add(entitlement)
        await self.session.flush()
        return entitlement

    async def get(self, tenant_id: UUID, entitlement_key: str) -> TenantEntitlementModel | None:
        result = await self.session.execute(
            select(TenantEntitlementModel).where(
                TenantEntitlementModel.tenant_id == tenant_id,
                TenantEntitlementModel.entitlement_key == entitlement_key,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: UUID) -> list[TenantEntitlementModel]:
        result = await self.session.execute(
            select(TenantEntitlementModel)
            .where(TenantEntitlementModel.tenant_id == tenant_id)
            .order_by(TenantEntitlementModel.entitlement_key)
        )
        return list(result.scalars().all())
