from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.feature_flags.infrastructure.models import FeatureFlagModel


class SQLAlchemyFeatureFlagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, feature_flag: FeatureFlagModel) -> FeatureFlagModel:
        self.session.add(feature_flag)
        await self.session.flush()
        return feature_flag

    async def get_by_id(self, flag_id: UUID) -> FeatureFlagModel | None:
        result = await self.session.execute(
            select(FeatureFlagModel).where(FeatureFlagModel.id == flag_id)
        )
        return result.scalar_one_or_none()

    async def get_by_tenant_and_key(
        self, tenant_id: UUID | None, feature_key: str
    ) -> FeatureFlagModel | None:
        result = await self.session.execute(
            select(FeatureFlagModel).where(
                FeatureFlagModel.tenant_id == tenant_id,
                FeatureFlagModel.feature_key == feature_key,
            )
        )
        return result.scalar_one_or_none()

    async def list_by_tenant(self, tenant_id: UUID | None) -> list[FeatureFlagModel]:
        result = await self.session.execute(
            select(FeatureFlagModel)
            .where(FeatureFlagModel.tenant_id == tenant_id)
            .order_by(FeatureFlagModel.feature_key)
        )
        return list(result.scalars().all())
