import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.inventory.application.warehouse_zone_use_cases import (
    CreateWarehouseZone,
    DeleteWarehouseZone,
    GetWarehouseZone,
    ListWarehouseZones,
    ReorderWarehouseZone,
    UpdateWarehouseZone,
    WarehouseZoneCreateInput,
    WarehouseZoneListInput,
    WarehouseZoneReorderInput,
    WarehouseZoneUpdateInput,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseError,
    WarehouseInactiveError,
    WarehouseNotFoundError,
    WarehouseZoneBranchRequiredError,
    WarehouseZoneCodeAlreadyExistsError,
    WarehouseZoneError,
    WarehouseZoneInvalidDataError,
    WarehouseZoneNotFoundError,
)
from app.modules.inventory.infrastructure.models import WarehouseZoneModel
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.inventory.infrastructure.warehouse_zone_repositories import (
    SQLAlchemyWarehouseZoneRepository,
)
from app.modules.inventory.presentation.warehouse_zone_schemas import (
    WarehouseZoneCreateRequest,
    WarehouseZoneReorderRequest,
    WarehouseZoneResponse,
    WarehouseZoneUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/warehouse-zones", tags=["Warehouse Zones"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
OptionalBoolQuery = Annotated[bool | None, Query()]
OptionalUUIDQuery = Annotated[UUID | None, Query()]


def _zone_response(zone: WarehouseZoneModel) -> WarehouseZoneResponse:
    return WarehouseZoneResponse(
        id=zone.id,
        tenant_id=zone.tenant_id,
        branch_id=zone.branch_id,
        warehouse_id=zone.warehouse_id,
        code=zone.code,
        name=zone.name,
        description=zone.description,
        type=zone.type,
        color=zone.color,
        icon=zone.icon,
        sort_order=zone.sort_order,
        is_receiving=zone.is_receiving,
        is_shipping=zone.is_shipping,
        is_storage=zone.is_storage,
        is_production=zone.is_production,
        is_quarantine=zone.is_quarantine,
        status=zone.status,
        is_active=zone.is_active,
        created_at=zone.created_at,
        updated_at=zone.updated_at,
    )


def _snapshot(zone: WarehouseZoneModel) -> dict[str, str | int | bool | None]:
    return {
        "id": str(zone.id),
        "tenant_id": str(zone.tenant_id),
        "branch_id": str(zone.branch_id),
        "warehouse_id": str(zone.warehouse_id),
        "code": zone.code,
        "name": zone.name,
        "description": zone.description,
        "type": zone.type.value,
        "color": zone.color,
        "icon": zone.icon,
        "sort_order": zone.sort_order,
        "is_receiving": zone.is_receiving,
        "is_shipping": zone.is_shipping,
        "is_storage": zone.is_storage,
        "is_production": zone.is_production,
        "is_quarantine": zone.is_quarantine,
        "status": zone.status.value,
        "is_active": zone.is_active,
    }


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _repositories(
    session: AsyncSession,
) -> tuple[SQLAlchemyWarehouseZoneRepository, SQLAlchemyWarehouseRepository]:
    return SQLAlchemyWarehouseZoneRepository(session), SQLAlchemyWarehouseRepository(session)


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _record_zone_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    zone: WarehouseZoneModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="inventory",
            action=action,
            entity_type="warehouse_zone",
            entity_id=zone.id,
            tenant_id=zone.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.get("", response_model=list[WarehouseZoneResponse])
async def list_warehouse_zones(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    warehouse_id: OptionalUUIDQuery = None,
    is_active: OptionalBoolQuery = None,
) -> JSONResponse:
    zones, _ = _repositories(session)
    result = await ListWarehouseZones(zones).execute(
        WarehouseZoneListInput(
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            warehouse_id=warehouse_id,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
    )
    logger.info(
        "warehouse_zone.query.completed",
        extra={"event": "warehouse_zone.query.completed", "tenant_id": str(current_user.tenant_id)},
    )
    return success_response(
        "WAREHOUSE_ZONE_LIST_RETRIEVED",
        data=[_zone_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{zone_id}", response_model=WarehouseZoneResponse)
async def get_warehouse_zone(
    zone_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        zones, _ = _repositories(session)
        zone = await GetWarehouseZone(zones).execute(zone_id, tenant_id=current_user.tenant_id)
        return success_response(
            "WAREHOUSE_ZONE_RETRIEVED",
            data=_zone_response(zone).model_dump(mode="json"),
        )
    except (WarehouseZoneError, WarehouseError) as exc:
        return warehouse_zone_exception_to_response(exc)


@router.post("", response_model=WarehouseZoneResponse)
async def create_warehouse_zone(
    payload: WarehouseZoneCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        zones, warehouses = _repositories(session)
        zone = await CreateWarehouseZone(zones, warehouses).execute(
            WarehouseZoneCreateInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                warehouse_id=payload.warehouse_id,
                code=payload.code,
                name=payload.name,
                description=payload.description,
                type=payload.type,
                color=payload.color,
                icon=payload.icon,
                sort_order=payload.sort_order,
                is_receiving=payload.is_receiving,
                is_shipping=payload.is_shipping,
                is_storage=payload.is_storage,
                is_production=payload.is_production,
                is_quarantine=payload.is_quarantine,
                is_active=payload.is_active,
                actor_id=current_user.id,
            )
        )
        await _record_zone_event(
            session,
            event_name="warehouse_zone.created",
            action="created",
            zone=zone,
            current_user=current_user,
            after_data=_snapshot(zone),
        )
        audit_logger.info(
            "warehouse_zone.created",
            extra={
                "event": "warehouse_zone.created",
                "tenant_id": str(current_user.tenant_id),
                "warehouse_zone_id": str(zone.id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_ZONE_CREATED",
            data=_zone_response(zone).model_dump(mode="json"),
        )
    except (WarehouseZoneError, WarehouseError) as exc:
        await session.rollback()
        return warehouse_zone_exception_to_response(exc)


@router.put("/{zone_id}", response_model=WarehouseZoneResponse)
async def update_warehouse_zone(
    zone_id: UUID,
    payload: WarehouseZoneUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        zones, warehouses = _repositories(session)
        current = await GetWarehouseZone(zones).execute(zone_id, tenant_id=current_user.tenant_id)
        before = _snapshot(current)
        zone = await UpdateWarehouseZone(zones, warehouses).execute(
            zone_id,
            tenant_id=current_user.tenant_id,
            input_data=WarehouseZoneUpdateInput(
                code=payload.code,
                name=payload.name,
                description=payload.description,
                type=payload.type,
                color=payload.color,
                icon=payload.icon,
                sort_order=payload.sort_order,
                is_receiving=payload.is_receiving,
                is_shipping=payload.is_shipping,
                is_storage=payload.is_storage,
                is_production=payload.is_production,
                is_quarantine=payload.is_quarantine,
                is_active=payload.is_active,
                actor_id=current_user.id,
            ),
        )
        await _record_zone_event(
            session,
            event_name="warehouse_zone.updated",
            action="updated",
            zone=zone,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(zone),
        )
        audit_logger.info(
            "warehouse_zone.updated",
            extra={"event": "warehouse_zone.updated", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_ZONE_UPDATED",
            data=_zone_response(zone).model_dump(mode="json"),
        )
    except (WarehouseZoneError, WarehouseError) as exc:
        await session.rollback()
        return warehouse_zone_exception_to_response(exc)


@router.post("/{zone_id}/reorder", response_model=WarehouseZoneResponse)
async def reorder_warehouse_zone(
    zone_id: UUID,
    payload: WarehouseZoneReorderRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        zones, _ = _repositories(session)
        zone = await ReorderWarehouseZone(zones).execute(
            zone_id,
            tenant_id=current_user.tenant_id,
            input_data=WarehouseZoneReorderInput(
                sort_order=payload.sort_order,
                actor_id=current_user.id,
            ),
        )
        await _record_zone_event(
            session,
            event_name="warehouse_zone.reordered",
            action="reordered",
            zone=zone,
            current_user=current_user,
            after_data=_snapshot(zone),
        )
        audit_logger.info(
            "warehouse_zone.reordered",
            extra={"event": "warehouse_zone.reordered", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_ZONE_REORDERED",
            data=_zone_response(zone).model_dump(mode="json"),
        )
    except (WarehouseZoneError, WarehouseError) as exc:
        await session.rollback()
        return warehouse_zone_exception_to_response(exc)


@router.delete("/{zone_id}", response_model=WarehouseZoneResponse)
async def delete_warehouse_zone(
    zone_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        zones, _ = _repositories(session)
        zone = await DeleteWarehouseZone(zones).execute(
            zone_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_zone_event(
            session,
            event_name="warehouse_zone.deleted",
            action="deleted",
            zone=zone,
            current_user=current_user,
            after_data=_snapshot(zone),
        )
        audit_logger.info(
            "warehouse_zone.deleted",
            extra={"event": "warehouse_zone.deleted", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_ZONE_DELETED",
            data=_zone_response(zone).model_dump(mode="json"),
        )
    except (WarehouseZoneError, WarehouseError) as exc:
        await session.rollback()
        return warehouse_zone_exception_to_response(exc)


def warehouse_zone_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, WarehouseZoneNotFoundError):
        return error_response("WAREHOUSE_ZONE_NOT_FOUND")
    if isinstance(exc, WarehouseZoneCodeAlreadyExistsError):
        return error_response("WAREHOUSE_ZONE_CODE_ALREADY_EXISTS")
    if isinstance(exc, WarehouseZoneBranchRequiredError | WarehouseBranchRequiredError):
        return error_response("WAREHOUSE_ZONE_BRANCH_REQUIRED")
    if isinstance(exc, WarehouseZoneInvalidDataError):
        return error_response("WAREHOUSE_ZONE_INVALID_DATA")
    if isinstance(exc, WarehouseNotFoundError):
        return error_response("WAREHOUSE_NOT_FOUND")
    if isinstance(exc, WarehouseInactiveError):
        return error_response("WAREHOUSE_INACTIVE")
    return error_response("INTERNAL_SERVER_ERROR")
