from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.entitlements.infrastructure.models import TenantEntitlementModel
from app.modules.entitlements.infrastructure.repositories import SQLAlchemyEntitlementRepository
from app.modules.plan.domain.exceptions import PlanInactiveError, PlanNotFoundError
from app.modules.plan.infrastructure.repositories import SQLAlchemyPlanRepository
from app.modules.subscription.domain.entities import SubscriptionChangeType, SubscriptionStatus
from app.modules.subscription.domain.exceptions import (
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.modules.subscription.infrastructure.models import SubscriptionModel
from app.modules.subscription.infrastructure.repositories import SQLAlchemySubscriptionRepository


@dataclass(frozen=True)
class SubscriptionCreateInput:
    tenant_id: UUID
    plan_id: UUID
    status: SubscriptionStatus
    billing_provider: str
    actor_id: UUID | None
    grace_period_days: int = 7


class CreateSubscription:
    def __init__(
        self,
        subscriptions: SQLAlchemySubscriptionRepository,
        plans: SQLAlchemyPlanRepository,
        entitlements: SQLAlchemyEntitlementRepository,
    ) -> None:
        self.subscriptions = subscriptions
        self.plans = plans
        self.entitlements = entitlements

    async def execute(self, input_data: SubscriptionCreateInput) -> SubscriptionModel:
        if await self.subscriptions.get_by_tenant(input_data.tenant_id):
            raise SubscriptionAlreadyExistsError("Subscription already exists.")
        plan = await self.plans.get_by_id(input_data.plan_id)
        if plan is None:
            raise PlanNotFoundError("Plan not found.")
        if not plan.is_active or plan.status != "active":
            raise PlanInactiveError("Plan inactive.")
        now = datetime.now(UTC)
        subscription = SubscriptionModel(
            tenant_id=input_data.tenant_id,
            plan_id=plan.id,
            status=input_data.status.value,
            billing_provider=input_data.billing_provider,
            started_at=now,
            trial_ends_at=now + timedelta(days=plan.trial_days)
            if input_data.status == SubscriptionStatus.TRIAL and plan.trial_days > 0
            else None,
            current_period_starts_at=now,
            current_period_ends_at=now + timedelta(days=30),
            grace_period_days=max(input_data.grace_period_days, 0),
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            await self.subscriptions.add(subscription)
            await project_plan_entitlements(
                plans=self.plans,
                entitlements=self.entitlements,
                subscription=subscription,
                actor_id=input_data.actor_id,
            )
            return subscription
        except IntegrityError as exc:
            raise SubscriptionAlreadyExistsError("Subscription already exists.") from exc


class GetCurrentSubscription:
    def __init__(self, subscriptions: SQLAlchemySubscriptionRepository) -> None:
        self.subscriptions = subscriptions

    async def execute(self, tenant_id: UUID) -> SubscriptionModel:
        subscription = await self.subscriptions.get_by_tenant(tenant_id)
        if subscription is None:
            raise SubscriptionNotFoundError("Subscription not found.")
        return subscription


class ChangeSubscriptionPlan:
    def __init__(
        self,
        subscriptions: SQLAlchemySubscriptionRepository,
        plans: SQLAlchemyPlanRepository,
        entitlements: SQLAlchemyEntitlementRepository,
    ) -> None:
        self.subscriptions = subscriptions
        self.plans = plans
        self.entitlements = entitlements

    async def execute(
        self, subscription_id: UUID, *, plan_id: UUID, actor_id: UUID | None = None
    ) -> tuple[SubscriptionModel, SubscriptionChangeType]:
        subscription = await self.subscriptions.get_by_id(subscription_id)
        if subscription is None:
            raise SubscriptionNotFoundError("Subscription not found.")
        current_plan = await self.plans.get_by_id(subscription.plan_id)
        next_plan = await self.plans.get_by_id(plan_id)
        if next_plan is None:
            raise PlanNotFoundError("Plan not found.")
        if not next_plan.is_active or next_plan.status != "active":
            raise PlanInactiveError("Plan inactive.")
        change_type = SubscriptionChangeType.CHANGE
        if current_plan is not None and next_plan.display_order > current_plan.display_order:
            change_type = SubscriptionChangeType.UPGRADE
        if current_plan is not None and next_plan.display_order < current_plan.display_order:
            change_type = SubscriptionChangeType.DOWNGRADE
        subscription.plan_id = next_plan.id
        subscription.updated_by = actor_id
        await self.subscriptions.add(subscription)
        await project_plan_entitlements(
            plans=self.plans,
            entitlements=self.entitlements,
            subscription=subscription,
            actor_id=actor_id,
        )
        return subscription, change_type


class ChangeSubscriptionStatus:
    def __init__(self, subscriptions: SQLAlchemySubscriptionRepository) -> None:
        self.subscriptions = subscriptions

    async def execute(
        self,
        subscription_id: UUID,
        *,
        status: SubscriptionStatus,
        actor_id: UUID | None = None,
    ) -> SubscriptionModel:
        subscription = await self.subscriptions.get_by_id(subscription_id)
        if subscription is None:
            raise SubscriptionNotFoundError("Subscription not found.")
        subscription.status = status.value
        subscription.updated_by = actor_id
        now = datetime.now(UTC)
        if status == SubscriptionStatus.PAST_DUE:
            subscription.grace_period_ends_at = now + timedelta(days=subscription.grace_period_days)
        if status == SubscriptionStatus.CANCELLED:
            subscription.cancelled_at = now
        return await self.subscriptions.add(subscription)


async def project_plan_entitlements(
    *,
    plans: SQLAlchemyPlanRepository,
    entitlements: SQLAlchemyEntitlementRepository,
    subscription: SubscriptionModel,
    actor_id: UUID | None,
) -> None:
    for plan_entitlement in await plans.list_entitlements(subscription.plan_id):
        existing = await entitlements.get(subscription.tenant_id, plan_entitlement.entitlement_key)
        if existing is None:
            existing = TenantEntitlementModel(
                tenant_id=subscription.tenant_id,
                subscription_id=subscription.id,
                entitlement_key=plan_entitlement.entitlement_key,
                entitlement_type=plan_entitlement.entitlement_type,
                source="plan",
                created_by=actor_id,
            )
        existing.subscription_id = subscription.id
        existing.is_enabled = plan_entitlement.is_enabled
        existing.updated_by = actor_id
        await entitlements.add(existing)
