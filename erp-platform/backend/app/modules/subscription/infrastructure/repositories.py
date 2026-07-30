from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.subscription.infrastructure.models import SubscriptionModel


class SQLAlchemySubscriptionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, subscription: SubscriptionModel) -> SubscriptionModel:
        self.session.add(subscription)
        await self.session.flush()
        return subscription

    async def get_by_id(self, subscription_id: UUID) -> SubscriptionModel | None:
        result = await self.session.execute(
            select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID) -> SubscriptionModel | None:
        result = await self.session.execute(
            select(SubscriptionModel).where(SubscriptionModel.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()
