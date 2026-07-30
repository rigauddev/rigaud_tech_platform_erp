import logging
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.plan.application.use_cases import (
    CreatePlan,
    ListPlans,
    PlanCreateInput,
    PlanEntitlementInput,
    PlanLimitInput,
)
from app.modules.plan.domain.exceptions import PlanAlreadyExistsError, PlanError, PlanNotFoundError
from app.modules.plan.infrastructure.repositories import SQLAlchemyPlanRepository
from app.modules.plan.presentation.schemas import PlanCreateRequest, PlanResponse
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/plans", tags=["SaaS Plans"])
logger = logging.getLogger("application")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]


def _require_platform_admin(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _plan_response(plan) -> PlanResponse:
    return PlanResponse.model_validate(plan)


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    payload: PlanCreateRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    logger.info("plan.creation.started", extra={"event": "plan.creation.started"})
    try:
        plan = await CreatePlan(SQLAlchemyPlanRepository(session)).execute(
            PlanCreateInput(
                code=payload.code,
                name=payload.name,
                description=payload.description,
                monthly_price=Decimal(payload.monthly_price),
                annual_price=Decimal(payload.annual_price),
                trial_days=payload.trial_days,
                is_trial_available=payload.is_trial_available,
                display_order=payload.display_order,
                is_active=payload.is_active,
                actor_id=current_user.id,
                entitlements=[
                    PlanEntitlementInput(**entitlement.model_dump())
                    for entitlement in payload.entitlements
                ],
                limits=[PlanLimitInput(**limit.model_dump()) for limit in payload.limits],
            )
        )
        await session.commit()
        logger.info("plan.creation.completed", extra={"event": "plan.creation.completed"})
        return success_response("PLAN_CREATED", data=_plan_response(plan).model_dump(mode="json"))
    except PlanError as exc:
        await session.rollback()
        return plan_exception_to_response(exc)


@router.get("", response_model=list[PlanResponse])
async def list_plans(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    active_only: bool = False,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    items, total, page, page_size = await ListPlans(SQLAlchemyPlanRepository(session)).execute(
        page=page, page_size=page_size, active_only=active_only
    )
    return success_response(
        "PLAN_LIST_RETRIEVED",
        data=[_plan_response(plan).model_dump(mode="json") for plan in items],
        meta=PaginationMeta.from_total(page=page, page_size=page_size, total=total),
    )


def plan_exception_to_response(exc: PlanError) -> JSONResponse:
    if isinstance(exc, PlanNotFoundError):
        return error_response("PLAN_NOT_FOUND")
    if isinstance(exc, PlanAlreadyExistsError):
        return error_response("PLAN_ALREADY_EXISTS")
    return error_response("VALIDATION_ERROR")
