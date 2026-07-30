import logging
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.billing.application.use_cases import BillingEventInput, RecordBillingEvent
from app.modules.billing.infrastructure.repositories import SQLAlchemyBillingEventRepository
from app.modules.billing.presentation.schemas import BillingEventRequest, BillingEventResponse
from app.shared.api.responses import error_response, success_response

router = APIRouter(prefix="/billing", tags=["SaaS Billing"])
logger = logging.getLogger("application")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


def _require_platform_admin(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


@router.post("/events/fake", response_model=BillingEventResponse)
async def fake_billing_event(
    payload: BillingEventRequest,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_platform_admin(current_user):
        return error
    billing_event = await RecordBillingEvent(SQLAlchemyBillingEventRepository(session)).execute(
        BillingEventInput(
            tenant_id=payload.tenant_id,
            subscription_id=payload.subscription_id,
            event_type=payload.event_type,
            payload=payload.payload,
            external_event_id=payload.external_event_id,
            actor_id=current_user.id,
        )
    )
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="billing.event",
            module="billing",
            action=billing_event.event_type,
            entity_type="billing_event",
            entity_id=billing_event.id,
            tenant_id=billing_event.tenant_id,
            actor_user_id=current_user.id,
            after_data={"event_type": billing_event.event_type, "status": billing_event.status},
        )
    )
    await session.commit()
    logger.info("billing.event", extra={"event": "billing.event"})
    return success_response(
        "BILLING_EVENT_RECORDED",
        data=BillingEventResponse.model_validate(billing_event).model_dump(mode="json"),
    )
