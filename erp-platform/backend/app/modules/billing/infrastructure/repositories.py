from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.billing.infrastructure.models import BillingEventModel


class SQLAlchemyBillingEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, billing_event: BillingEventModel) -> BillingEventModel:
        self.session.add(billing_event)
        await self.session.flush()
        return billing_event

    async def list_by_tenant(self, tenant_id: UUID) -> list[BillingEventModel]:
        result = await self.session.execute(
            select(BillingEventModel)
            .where(BillingEventModel.tenant_id == tenant_id)
            .order_by(BillingEventModel.created_at.desc())
        )
        return list(result.scalars().all())
