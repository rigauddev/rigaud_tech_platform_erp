import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.billing.application.providers import FakeBillingProvider
from app.modules.entitlements.infrastructure.repositories import SQLAlchemyEntitlementRepository
from app.modules.plan.domain.exceptions import PlanError, PlanInactiveError, PlanNotFoundError
from app.modules.plan.infrastructure.repositories import SQLAlchemyPlanRepository
from app.modules.subscription.application.use_cases import (
    ChangeSubscriptionPlan,
    ChangeSubscriptionStatus,
    CreateSubscription,
    GetCurrentSubscription,
    SubscriptionCreateInput,
)
from app.modules.subscription.domain.exceptions import (
    SubscriptionAlreadyExistsError,
    SubscriptionError,
    SubscriptionNotFoundError,
)
from app.modules.subscription.infrastructure.repositories import SQLAlchemySubscriptionRepository
from app.modules.subscription.presentation.schemas import (
    SubscriptionChangePlanRequest,
    SubscriptionCreateRequest,
    SubscriptionResponse,
    SubscriptionStatusRequest,
)
from app.shared.api.responses import error_response, success_response

router = APIRouter(prefix="/subscriptions", tags=["SaaS Subscriptions"])
logger = logging.getLogger("application")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


def _require_platform_admin(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _subscription_response(subscription) -> SubscriptionResponse:
    return SubscriptionResponse.model_validate(subscription)


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


@router.post("", response_model=SubscriptionResponse)
async def create_subscription(
    payload: SubscriptionCreateRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    logger.info("subscription.created", extra={"event": "subscription.created"})
    try:
        fake_provider = FakeBillingProvider()
        provider_result = await fake_provider.create_subscription(
            payload.tenant_id, payload.plan_id
        )
        subscription = await CreateSubscription(
            SQLAlchemySubscriptionRepository(session),
            SQLAlchemyPlanRepository(session),
            SQLAlchemyEntitlementRepository(session),
        ).execute(
            SubscriptionCreateInput(
                tenant_id=payload.tenant_id,
                plan_id=payload.plan_id,
                status=payload.status,
                billing_provider=provider_result.provider.value,
                actor_id=current_user.id,
                grace_period_days=payload.grace_period_days,
            )
        )
        subscription.external_reference = provider_result.external_reference
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="subscription.created",
                module="subscription",
                action="created",
                entity_type="subscription",
                entity_id=subscription.id,
                tenant_id=subscription.tenant_id,
                actor_user_id=current_user.id,
                after_data={"plan_id": str(subscription.plan_id), "status": subscription.status},
            )
        )
        await session.commit()
        return success_response(
            "SUBSCRIPTION_CREATED",
            data=_subscription_response(subscription).model_dump(mode="json"),
        )
    except (SubscriptionError, PlanError) as exc:
        await session.rollback()
        return subscription_exception_to_response(exc)


@router.get("/current", response_model=SubscriptionResponse)
async def current_subscription(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        subscription = await GetCurrentSubscription(
            SQLAlchemySubscriptionRepository(session)
        ).execute(current_user.tenant_id)
        return success_response(
            "SUBSCRIPTION_RETRIEVED",
            data=_subscription_response(subscription).model_dump(mode="json"),
        )
    except SubscriptionError as exc:
        return subscription_exception_to_response(exc)


@router.post("/{subscription_id}/change-plan", response_model=SubscriptionResponse)
async def change_plan(
    subscription_id: UUID,
    payload: SubscriptionChangePlanRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    try:
        subscription, change_type = await ChangeSubscriptionPlan(
            SQLAlchemySubscriptionRepository(session),
            SQLAlchemyPlanRepository(session),
            SQLAlchemyEntitlementRepository(session),
        ).execute(subscription_id, plan_id=payload.plan_id, actor_id=current_user.id)
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="plan.changed",
                module="subscription",
                action=change_type.value,
                entity_type="subscription",
                entity_id=subscription.id,
                tenant_id=subscription.tenant_id,
                actor_user_id=current_user.id,
                after_data={"plan_id": str(subscription.plan_id)},
            )
        )
        await session.commit()
        return success_response(
            "SUBSCRIPTION_PLAN_CHANGED",
            data=_subscription_response(subscription).model_dump(mode="json"),
        )
    except (SubscriptionError, PlanError) as exc:
        await session.rollback()
        return subscription_exception_to_response(exc)


@router.post("/{subscription_id}/billing-status", response_model=SubscriptionResponse)
async def change_billing_status(
    subscription_id: UUID,
    payload: SubscriptionStatusRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    try:
        subscription = await ChangeSubscriptionStatus(
            SQLAlchemySubscriptionRepository(session)
        ).execute(subscription_id, status=payload.status, actor_id=current_user.id)
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="subscription.updated",
                module="subscription",
                action="billing_status_changed",
                entity_type="subscription",
                entity_id=subscription.id,
                tenant_id=subscription.tenant_id,
                actor_user_id=current_user.id,
                after_data={"status": subscription.status},
            )
        )
        await session.commit()
        return success_response(
            "SUBSCRIPTION_STATUS_CHANGED",
            data=_subscription_response(subscription).model_dump(mode="json"),
        )
    except SubscriptionError as exc:
        await session.rollback()
        return subscription_exception_to_response(exc)


def subscription_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, SubscriptionNotFoundError):
        return error_response("SUBSCRIPTION_NOT_FOUND")
    if isinstance(exc, SubscriptionAlreadyExistsError):
        return error_response("SUBSCRIPTION_ALREADY_EXISTS")
    if isinstance(exc, PlanNotFoundError):
        return error_response("PLAN_NOT_FOUND")
    if isinstance(exc, PlanInactiveError):
        return error_response("PLAN_INACTIVE")
    return error_response("VALIDATION_ERROR")
