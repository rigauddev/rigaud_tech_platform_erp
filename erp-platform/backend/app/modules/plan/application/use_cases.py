from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.plan.domain.exceptions import PlanAlreadyExistsError, PlanNotFoundError
from app.modules.plan.infrastructure.models import PlanEntitlementModel, PlanLimitModel, PlanModel
from app.modules.plan.infrastructure.repositories import SQLAlchemyPlanRepository


@dataclass(frozen=True)
class PlanEntitlementInput:
    entitlement_key: str
    entitlement_type: str
    is_enabled: bool = True


@dataclass(frozen=True)
class PlanLimitInput:
    limit_key: str
    limit_value: int
    is_unlimited: bool = False


@dataclass(frozen=True)
class PlanCreateInput:
    code: str
    name: str
    description: str | None
    monthly_price: Decimal
    annual_price: Decimal
    trial_days: int
    is_trial_available: bool
    display_order: int
    is_active: bool
    actor_id: UUID | None
    entitlements: list[PlanEntitlementInput]
    limits: list[PlanLimitInput]


class CreatePlan:
    def __init__(self, plans: SQLAlchemyPlanRepository) -> None:
        self.plans = plans

    async def execute(self, input_data: PlanCreateInput) -> PlanModel:
        existing = await self.plans.get_by_code(_normalize_key(input_data.code))
        if existing is not None:
            raise PlanAlreadyExistsError("Plan already exists.")
        plan = PlanModel(
            code=_normalize_key(input_data.code),
            name=input_data.name.strip(),
            description=input_data.description.strip() if input_data.description else None,
            monthly_price=input_data.monthly_price,
            annual_price=input_data.annual_price,
            trial_days=max(input_data.trial_days, 0),
            is_trial_available=input_data.is_trial_available,
            is_active=input_data.is_active,
            display_order=max(input_data.display_order, 0),
            status="active" if input_data.is_active else "inactive",
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            await self.plans.add(plan)
            for entitlement in input_data.entitlements:
                await self.plans.add_entitlement(
                    PlanEntitlementModel(
                        plan_id=plan.id,
                        entitlement_key=_normalize_key(entitlement.entitlement_key),
                        entitlement_type=_normalize_key(entitlement.entitlement_type),
                        is_enabled=entitlement.is_enabled,
                        created_by=input_data.actor_id,
                        updated_by=input_data.actor_id,
                    )
                )
            for limit in input_data.limits:
                await self.plans.add_limit(
                    PlanLimitModel(
                        plan_id=plan.id,
                        limit_key=_normalize_key(limit.limit_key),
                        limit_value=-1 if limit.is_unlimited else max(limit.limit_value, 0),
                        is_unlimited=limit.is_unlimited,
                        created_by=input_data.actor_id,
                        updated_by=input_data.actor_id,
                    )
                )
            return plan
        except IntegrityError as exc:
            raise PlanAlreadyExistsError("Plan already exists.") from exc


class GetPlan:
    def __init__(self, plans: SQLAlchemyPlanRepository) -> None:
        self.plans = plans

    async def execute(self, plan_id: UUID) -> PlanModel:
        plan = await self.plans.get_by_id(plan_id)
        if plan is None:
            raise PlanNotFoundError("Plan not found.")
        return plan


class ListPlans:
    def __init__(self, plans: SQLAlchemyPlanRepository) -> None:
        self.plans = plans

    async def execute(
        self, *, page: int, page_size: int, active_only: bool = False
    ) -> tuple[list[PlanModel], int, int, int]:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        offset = (page - 1) * page_size
        items = await self.plans.list(limit=page_size, offset=offset, active_only=active_only)
        total = await self.plans.count(active_only=active_only)
        return items, total, page, page_size


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")
