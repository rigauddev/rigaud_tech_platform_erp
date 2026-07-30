from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.plan.infrastructure.models import PlanEntitlementModel, PlanLimitModel, PlanModel


class SQLAlchemyPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, plan: PlanModel) -> PlanModel:
        self.session.add(plan)
        await self.session.flush()
        return plan

    async def add_entitlement(self, entitlement: PlanEntitlementModel) -> PlanEntitlementModel:
        self.session.add(entitlement)
        await self.session.flush()
        return entitlement

    async def add_limit(self, limit: PlanLimitModel) -> PlanLimitModel:
        self.session.add(limit)
        await self.session.flush()
        return limit

    async def get_by_id(self, plan_id: UUID) -> PlanModel | None:
        result = await self.session.execute(
            select(PlanModel).where(PlanModel.id == plan_id, PlanModel.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, code: str) -> PlanModel | None:
        result = await self.session.execute(
            select(PlanModel).where(PlanModel.code == code, PlanModel.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list(self, *, limit: int, offset: int, active_only: bool = False) -> list[PlanModel]:
        statement = select(PlanModel).where(PlanModel.deleted_at.is_(None))
        if active_only:
            statement = statement.where(PlanModel.is_active.is_(True), PlanModel.status == "active")
        result = await self.session.execute(
            statement.order_by(PlanModel.display_order, PlanModel.name).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def count(self, *, active_only: bool = False) -> int:
        statement = select(PlanModel.id).where(PlanModel.deleted_at.is_(None))
        if active_only:
            statement = statement.where(PlanModel.is_active.is_(True), PlanModel.status == "active")
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def list_entitlements(self, plan_id: UUID) -> list[PlanEntitlementModel]:
        result = await self.session.execute(
            select(PlanEntitlementModel)
            .where(PlanEntitlementModel.plan_id == plan_id)
            .order_by(PlanEntitlementModel.entitlement_key)
        )
        return list(result.scalars().all())

    async def list_limits(self, plan_id: UUID) -> list[PlanLimitModel]:
        result = await self.session.execute(
            select(PlanLimitModel)
            .where(PlanLimitModel.plan_id == plan_id)
            .order_by(PlanLimitModel.limit_key)
        )
        return list(result.scalars().all())
