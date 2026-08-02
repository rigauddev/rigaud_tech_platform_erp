import logging
from decimal import Decimal
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
from app.modules.inventory.application.warehouse_location_use_cases import (
    ActivateWarehouseLocation,
    CreateWarehouseLocation,
    DeactivateWarehouseLocation,
    DeleteWarehouseLocation,
    GetWarehouseLocation,
    ListWarehouseLocations,
    ReorderWarehouseLocation,
    UpdateWarehouseLocation,
    WarehouseLocationCreateInput,
    WarehouseLocationListInput,
    WarehouseLocationReorderInput,
    WarehouseLocationUpdateInput,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseError,
    WarehouseInactiveError,
    WarehouseLocationBarcodeAlreadyExistsError,
    WarehouseLocationBranchRequiredError,
    WarehouseLocationCodeAlreadyExistsError,
    WarehouseLocationError,
    WarehouseLocationInvalidDataError,
    WarehouseLocationNotFoundError,
    WarehouseLocationQrCodeAlreadyExistsError,
    WarehouseNotFoundError,
    WarehouseZoneError,
    WarehouseZoneInactiveError,
    WarehouseZoneNotFoundError,
)
from app.modules.inventory.infrastructure.models import WarehouseLocationModel
from app.modules.inventory.infrastructure.warehouse_location_repositories import (
    SQLAlchemyWarehouseLocationRepository,
)
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.inventory.infrastructure.warehouse_zone_repositories import (
    SQLAlchemyWarehouseZoneRepository,
)
from app.modules.inventory.presentation.warehouse_location_schemas import (
    WarehouseLocationCreateRequest,
    WarehouseLocationReorderRequest,
    WarehouseLocationResponse,
    WarehouseLocationUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/warehouse-locations", tags=["Warehouse Locations"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
OptionalBoolQuery = Annotated[bool | None, Query()]
OptionalUUIDQuery = Annotated[UUID | None, Query()]
OptionalSearchQuery = Annotated[str | None, Query(max_length=80)]


def _location_response(location: WarehouseLocationModel) -> WarehouseLocationResponse:
    return WarehouseLocationResponse(
        id=location.id,
        tenant_id=location.tenant_id,
        branch_id=location.branch_id,
        warehouse_id=location.warehouse_id,
        zone_id=location.zone_id,
        code=location.code,
        name=location.name,
        alias=location.alias,
        barcode=location.barcode,
        qr_code=location.qr_code,
        aisle=location.aisle,
        rack=location.rack,
        shelf=location.shelf,
        level=location.level,
        position=location.position,
        capacity=location.capacity,
        capacity_unit=location.capacity_unit,
        allow_negative=location.allow_negative,
        allow_mixed_items=location.allow_mixed_items,
        allow_expired=location.allow_expired,
        is_pick_location=location.is_pick_location,
        is_receive_location=location.is_receive_location,
        is_shipping_location=location.is_shipping_location,
        is_default=location.is_default,
        sort_order=location.sort_order,
        status=location.status,
        is_active=location.is_active,
        created_at=location.created_at,
        updated_at=location.updated_at,
    )


def _snapshot(location: WarehouseLocationModel) -> dict[str, str | int | bool | None]:
    return {
        "id": str(location.id),
        "tenant_id": str(location.tenant_id),
        "branch_id": str(location.branch_id),
        "warehouse_id": str(location.warehouse_id),
        "zone_id": str(location.zone_id),
        "code": location.code,
        "name": location.name,
        "alias": location.alias,
        "barcode": location.barcode,
        "qr_code": location.qr_code,
        "aisle": location.aisle,
        "rack": location.rack,
        "shelf": location.shelf,
        "level": location.level,
        "position": location.position,
        "capacity": _decimal_to_string(location.capacity),
        "capacity_unit": location.capacity_unit,
        "allow_negative": location.allow_negative,
        "allow_mixed_items": location.allow_mixed_items,
        "allow_expired": location.allow_expired,
        "is_pick_location": location.is_pick_location,
        "is_receive_location": location.is_receive_location,
        "is_shipping_location": location.is_shipping_location,
        "is_default": location.is_default,
        "sort_order": location.sort_order,
        "status": location.status.value,
        "is_active": location.is_active,
    }


def _decimal_to_string(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _repositories(
    session: AsyncSession,
) -> tuple[
    SQLAlchemyWarehouseLocationRepository,
    SQLAlchemyWarehouseRepository,
    SQLAlchemyWarehouseZoneRepository,
]:
    return (
        SQLAlchemyWarehouseLocationRepository(session),
        SQLAlchemyWarehouseRepository(session),
        SQLAlchemyWarehouseZoneRepository(session),
    )


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _record_location_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    location: WarehouseLocationModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="inventory",
            action=action,
            entity_type="warehouse_location",
            entity_id=location.id,
            tenant_id=location.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.get("", response_model=list[WarehouseLocationResponse])
async def list_warehouse_locations(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    warehouse_id: OptionalUUIDQuery = None,
    zone_id: OptionalUUIDQuery = None,
    search: OptionalSearchQuery = None,
    is_active: OptionalBoolQuery = None,
) -> JSONResponse:
    locations, _, _ = _repositories(session)
    result = await ListWarehouseLocations(locations).execute(
        WarehouseLocationListInput(
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            warehouse_id=warehouse_id,
            zone_id=zone_id,
            search=search,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
    )
    logger.info(
        "warehouse_location.query.completed",
        extra={
            "event": "warehouse_location.query.completed",
            "tenant_id": str(current_user.tenant_id),
        },
    )
    return success_response(
        "WAREHOUSE_LOCATION_LIST_RETRIEVED",
        data=[_location_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{location_id}", response_model=WarehouseLocationResponse)
async def get_warehouse_location(
    location_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        locations, _, _ = _repositories(session)
        location = await GetWarehouseLocation(locations).execute(
            location_id,
            tenant_id=current_user.tenant_id,
        )
        return success_response(
            "WAREHOUSE_LOCATION_RETRIEVED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        return warehouse_location_exception_to_response(exc)


@router.post("", response_model=WarehouseLocationResponse)
async def create_warehouse_location(
    payload: WarehouseLocationCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        locations, warehouses, zones = _repositories(session)
        location = await CreateWarehouseLocation(locations, warehouses, zones).execute(
            WarehouseLocationCreateInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                warehouse_id=payload.warehouse_id,
                zone_id=payload.zone_id,
                code=payload.code,
                name=payload.name,
                alias=payload.alias,
                barcode=payload.barcode,
                qr_code=payload.qr_code,
                aisle=payload.aisle,
                rack=payload.rack,
                shelf=payload.shelf,
                level=payload.level,
                position=payload.position,
                capacity=payload.capacity,
                capacity_unit=payload.capacity_unit,
                allow_negative=payload.allow_negative,
                allow_mixed_items=payload.allow_mixed_items,
                allow_expired=payload.allow_expired,
                is_pick_location=payload.is_pick_location,
                is_receive_location=payload.is_receive_location,
                is_shipping_location=payload.is_shipping_location,
                is_default=payload.is_default,
                sort_order=payload.sort_order,
                is_active=payload.is_active,
                actor_id=current_user.id,
            )
        )
        await _record_location_event(
            session,
            event_name="warehouse_location.created",
            action="created",
            location=location,
            current_user=current_user,
            after_data=_snapshot(location),
        )
        audit_logger.info(
            "warehouse_location.created",
            extra={
                "event": "warehouse_location.created",
                "tenant_id": str(current_user.tenant_id),
                "warehouse_location_id": str(location.id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_LOCATION_CREATED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        await session.rollback()
        return warehouse_location_exception_to_response(exc)


@router.put("/{location_id}", response_model=WarehouseLocationResponse)
async def update_warehouse_location(
    location_id: UUID,
    payload: WarehouseLocationUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        locations, warehouses, zones = _repositories(session)
        current = await GetWarehouseLocation(locations).execute(
            location_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        location = await UpdateWarehouseLocation(locations, warehouses, zones).execute(
            location_id,
            tenant_id=current_user.tenant_id,
            input_data=WarehouseLocationUpdateInput(
                code=payload.code,
                name=payload.name,
                alias=payload.alias,
                barcode=payload.barcode,
                qr_code=payload.qr_code,
                aisle=payload.aisle,
                rack=payload.rack,
                shelf=payload.shelf,
                level=payload.level,
                position=payload.position,
                capacity=payload.capacity,
                capacity_unit=payload.capacity_unit,
                allow_negative=payload.allow_negative,
                allow_mixed_items=payload.allow_mixed_items,
                allow_expired=payload.allow_expired,
                is_pick_location=payload.is_pick_location,
                is_receive_location=payload.is_receive_location,
                is_shipping_location=payload.is_shipping_location,
                is_default=payload.is_default,
                sort_order=payload.sort_order,
                is_active=payload.is_active,
                actor_id=current_user.id,
            ),
        )
        await _record_location_event(
            session,
            event_name="warehouse_location.updated",
            action="updated",
            location=location,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(location),
        )
        audit_logger.info(
            "warehouse_location.updated",
            extra={"event": "warehouse_location.updated", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_LOCATION_UPDATED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        await session.rollback()
        return warehouse_location_exception_to_response(exc)


@router.post("/{location_id}/activate", response_model=WarehouseLocationResponse)
async def activate_warehouse_location(
    location_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_location_status(
        location_id,
        request,
        session,
        current_user,
        activate=True,
    )


@router.post("/{location_id}/deactivate", response_model=WarehouseLocationResponse)
async def deactivate_warehouse_location(
    location_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_location_status(
        location_id,
        request,
        session,
        current_user,
        activate=False,
    )


@router.post("/{location_id}/reorder", response_model=WarehouseLocationResponse)
async def reorder_warehouse_location(
    location_id: UUID,
    payload: WarehouseLocationReorderRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        locations, _, _ = _repositories(session)
        location = await ReorderWarehouseLocation(locations).execute(
            location_id,
            tenant_id=current_user.tenant_id,
            input_data=WarehouseLocationReorderInput(
                sort_order=payload.sort_order,
                actor_id=current_user.id,
            ),
        )
        await _record_location_event(
            session,
            event_name="warehouse_location.reordered",
            action="reordered",
            location=location,
            current_user=current_user,
            after_data=_snapshot(location),
        )
        audit_logger.info(
            "warehouse_location.reordered",
            extra={"event": "warehouse_location.reordered", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_LOCATION_REORDERED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        await session.rollback()
        return warehouse_location_exception_to_response(exc)


@router.delete("/{location_id}", response_model=WarehouseLocationResponse)
async def delete_warehouse_location(
    location_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        locations, _, _ = _repositories(session)
        location = await DeleteWarehouseLocation(locations).execute(
            location_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_location_event(
            session,
            event_name="warehouse_location.deleted",
            action="deleted",
            location=location,
            current_user=current_user,
            after_data=_snapshot(location),
        )
        audit_logger.info(
            "warehouse_location.deleted",
            extra={"event": "warehouse_location.deleted", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_LOCATION_DELETED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        await session.rollback()
        return warehouse_location_exception_to_response(exc)


async def _change_location_status(
    location_id: UUID,
    request: Request,
    session: AsyncSession,
    current_user: AuthenticatedUser,
    *,
    activate: bool,
) -> JSONResponse:
    try:
        locations, _, _ = _repositories(session)
        current = await GetWarehouseLocation(locations).execute(
            location_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        use_case = (
            ActivateWarehouseLocation(locations)
            if activate
            else DeactivateWarehouseLocation(locations)
        )
        location = await use_case.execute(
            location_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        event_name = (
            "warehouse_location.activated" if activate else "warehouse_location.deactivated"
        )
        await _record_location_event(
            session,
            event_name=event_name,
            action="activated" if activate else "deactivated",
            location=location,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(location),
        )
        audit_logger.info(
            event_name,
            extra={"event": event_name, "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_LOCATION_ACTIVATED" if activate else "WAREHOUSE_LOCATION_DEACTIVATED",
            data=_location_response(location).model_dump(mode="json"),
        )
    except (WarehouseLocationError, WarehouseError, WarehouseZoneError) as exc:
        await session.rollback()
        return warehouse_location_exception_to_response(exc)


def warehouse_location_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, WarehouseLocationNotFoundError):
        return error_response("WAREHOUSE_LOCATION_NOT_FOUND")
    if isinstance(exc, WarehouseLocationCodeAlreadyExistsError):
        return error_response("WAREHOUSE_LOCATION_CODE_ALREADY_EXISTS")
    if isinstance(exc, WarehouseLocationBarcodeAlreadyExistsError):
        return error_response("WAREHOUSE_LOCATION_BARCODE_ALREADY_EXISTS")
    if isinstance(exc, WarehouseLocationQrCodeAlreadyExistsError):
        return error_response("WAREHOUSE_LOCATION_QR_CODE_ALREADY_EXISTS")
    if isinstance(exc, WarehouseLocationBranchRequiredError | WarehouseBranchRequiredError):
        return error_response("WAREHOUSE_LOCATION_BRANCH_REQUIRED")
    if isinstance(exc, WarehouseLocationInvalidDataError):
        return error_response("WAREHOUSE_LOCATION_INVALID_DATA")
    if isinstance(exc, WarehouseNotFoundError):
        return error_response("WAREHOUSE_NOT_FOUND")
    if isinstance(exc, WarehouseInactiveError):
        return error_response("WAREHOUSE_INACTIVE")
    if isinstance(exc, WarehouseZoneNotFoundError):
        return error_response("WAREHOUSE_ZONE_NOT_FOUND")
    if isinstance(exc, WarehouseZoneInactiveError):
        return error_response("WAREHOUSE_ZONE_INACTIVE")
    return error_response("INTERNAL_SERVER_ERROR")
