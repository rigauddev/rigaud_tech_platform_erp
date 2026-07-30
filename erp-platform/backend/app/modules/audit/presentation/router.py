from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.infrastructure.models import AuditEventModel
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.audit.presentation.schemas import AuditEventResponse
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/audit/events", tags=["Audit"])

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]


def _audit_event_response(event: AuditEventModel) -> dict:
    return AuditEventResponse(
        id=event.id,
        event_name=event.event_name,
        module=event.module,
        action=event.action,
        entity_type=event.entity_type,
        entity_id=event.entity_id,
        tenant_id=event.tenant_id,
        actor_user_id=event.actor_user_id,
        request_id=event.request_id,
        correlation_id=event.correlation_id,
        source=event.source,
        ip_address=event.ip_address,
        user_agent=event.user_agent,
        before_data=event.before_data,
        after_data=event.after_data,
        metadata=event.event_metadata,
        occurred_at=event.occurred_at,
        created_at=event.created_at,
    ).model_dump(mode="json")


@router.get("")
async def list_audit_events(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    tenant_id: UUID | None = None,
    actor_user_id: UUID | None = None,
    event_name: str | None = Query(default=None, max_length=120),
    module: str | None = Query(default=None, max_length=80),
    entity_type: str | None = Query(default=None, max_length=80),
    entity_id: str | None = Query(default=None, max_length=80),
    request_id: str | None = Query(default=None, max_length=36),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
):
    if not current_user.is_superuser:
        return error_response("AUTH_FORBIDDEN")
    repository = SQLAlchemyAuditEventRepository(session)
    offset = (page - 1) * page_size
    filters = {
        "tenant_id": tenant_id,
        "actor_user_id": actor_user_id,
        "event_name": event_name,
        "module": module,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "request_id": request_id,
        "date_from": date_from,
        "date_to": date_to,
    }
    items = await repository.list(limit=page_size, offset=offset, **filters)
    total = await repository.count(**filters)
    return success_response(
        "AUDIT_EVENTS_RETRIEVED",
        data=[_audit_event_response(item) for item in items],
        meta=PaginationMeta.from_total(page=page, page_size=page_size, total=total),
    )


@router.get("/{event_id}")
async def get_audit_event(
    event_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
):
    if not current_user.is_superuser:
        return error_response("AUTH_FORBIDDEN")
    event = await SQLAlchemyAuditEventRepository(session).get_by_id(event_id)
    if event is None:
        return error_response("AUDIT_EVENT_NOT_FOUND")
    return success_response("AUDIT_EVENT_RETRIEVED", data=_audit_event_response(event))
