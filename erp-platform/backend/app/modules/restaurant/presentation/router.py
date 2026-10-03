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
from app.modules.restaurant.application.sector_use_cases import (
    CreateRestaurantSector,
    DeleteRestaurantSector,
    GetRestaurantSector,
    ListRestaurantSectors,
    SectorInput,
    UpdateRestaurantSector,
)
from app.modules.restaurant.application.table_use_cases import (
    CreateRestaurantFloor,
    CreateRestaurantTable,
    DeleteRestaurantFloor,
    DeleteRestaurantTable,
    FloorInput,
    GetRestaurantFloor,
    GetRestaurantTable,
    ListRestaurantFloors,
    ListRestaurantTables,
    TableInput,
    UpdateRestaurantFloor,
    UpdateRestaurantTable,
)
from app.modules.restaurant.domain.exceptions import (
    RestaurantBranchRequiredError,
    RestaurantError,
    RestaurantFloorCodeAlreadyExistsError,
    RestaurantFloorNotFoundError,
    RestaurantInvalidDataError,
    RestaurantSectorCodeAlreadyExistsError,
    RestaurantSectorNotFoundError,
    RestaurantTableNotFoundError,
    RestaurantTableNumberAlreadyExistsError,
)
from app.modules.restaurant.infrastructure.models import (
    RestaurantFloorModel,
    RestaurantSectorModel,
    RestaurantTableModel,
)
from app.modules.restaurant.infrastructure.repositories import (
    SQLAlchemyRestaurantFloorRepository,
    SQLAlchemyRestaurantSectorRepository,
    SQLAlchemyRestaurantTableRepository,
)
from app.modules.restaurant.presentation.schemas import (
    RestaurantFloorRequest,
    RestaurantFloorResponse,
    RestaurantSectorRequest,
    RestaurantSectorResponse,
    RestaurantTableRequest,
    RestaurantTableResponse,
)
from app.shared.api.responses import error_response, success_response

router = APIRouter(prefix="/restaurant", tags=["Restaurant tables"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")
AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


def _floor_response(item: RestaurantFloorModel) -> RestaurantFloorResponse:
    return RestaurantFloorResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        branch_id=item.branch_id,
        code=item.code,
        name=item.name,
        description=item.description,
        sort_order=item.sort_order,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _sector_response(item: RestaurantSectorModel) -> RestaurantSectorResponse:
    return RestaurantSectorResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        branch_id=item.branch_id,
        floor_id=item.floor_id,
        code=item.code,
        name=item.name,
        description=item.description,
        type=item.type,
        color=item.color,
        icon=item.icon,
        sort_order=item.sort_order,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _table_response(item: RestaurantTableModel) -> RestaurantTableResponse:
    return RestaurantTableResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        branch_id=item.branch_id,
        floor_id=item.floor_id,
        number=item.number,
        name=item.name,
        capacity=item.capacity,
        position_x=item.position_x,
        position_y=item.position_y,
        width=item.width,
        height=item.height,
        shape=item.shape,
        status=item.status,
        qr_code=item.qr_code,
        sort_order=item.sort_order,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _floor_input(payload: RestaurantFloorRequest, user: AuthenticatedUser) -> FloorInput:
    return FloorInput(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        code=payload.code,
        name=payload.name,
        description=payload.description,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
        actor_id=user.id,
    )


def _sector_input(payload: RestaurantSectorRequest, user: AuthenticatedUser) -> SectorInput:
    return SectorInput(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        code=payload.code,
        name=payload.name,
        type=payload.type,
        floor_id=payload.floor_id,
        description=payload.description,
        color=payload.color,
        icon=payload.icon,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
        actor_id=user.id,
    )


def _table_input(payload: RestaurantTableRequest, user: AuthenticatedUser) -> TableInput:
    return TableInput(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        floor_id=payload.floor_id,
        number=payload.number,
        name=payload.name,
        capacity=payload.capacity,
        position_x=payload.position_x,
        position_y=payload.position_y,
        width=payload.width,
        height=payload.height,
        shape=payload.shape,
        status=payload.status,
        qr_code=payload.qr_code,
        sort_order=payload.sort_order,
        is_active=payload.is_active,
        actor_id=user.id,
    )


async def _audit(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    item: RestaurantFloorModel | RestaurantSectorModel | RestaurantTableModel,
    entity_type: str,
    user: AuthenticatedUser,
    request: Request,
) -> None:
    await AuditService(SQLAlchemyAuditEventRepository(session)).record_event(
        AuditEventInput(
            event_name=event_name,
            module="restaurant",
            action=action,
            entity_type=entity_type,
            entity_id=item.id,
            tenant_id=item.tenant_id,
            actor_user_id=user.id,
            after_data={
                "id": str(item.id),
                "branch_id": str(item.branch_id),
                "is_active": item.is_active,
            },
        )
    )
    audit_logger.info(
        event_name,
        extra={
            "event": event_name,
            "tenant_id": str(item.tenant_id),
            "request_id": request.headers.get("x-request-id"),
        },
    )


@router.get("/sectors", response_model=list[RestaurantSectorResponse])
async def list_sectors(
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
    is_active: bool | None = Query(default=None),
) -> JSONResponse:
    items = await ListRestaurantSectors(SQLAlchemyRestaurantSectorRepository(session)).execute(
        tenant_id=user.tenant_id, branch_id=user.branch_id, is_active=is_active
    )
    return success_response(
        "RESTAURANT_SECTOR_LIST_RETRIEVED",
        data=[_sector_response(item).model_dump(mode="json") for item in items],
    )


@router.get("/sectors/{sector_id}", response_model=RestaurantSectorResponse)
async def get_sector(
    sector_id: UUID,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await GetRestaurantSector(SQLAlchemyRestaurantSectorRepository(session)).execute(
            sector_id, tenant_id=user.tenant_id
        )
        return success_response(
            "RESTAURANT_SECTOR_RETRIEVED", data=_sector_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        return _error(exc)


@router.post("/sectors", response_model=RestaurantSectorResponse)
async def create_sector(
    payload: RestaurantSectorRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await CreateRestaurantSector(
            SQLAlchemyRestaurantSectorRepository(session),
            SQLAlchemyRestaurantFloorRepository(session),
        ).execute(_sector_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.sector.created",
            action="created",
            item=item,
            entity_type="restaurant_sector",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_SECTOR_CREATED", data=_sector_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.put("/sectors/{sector_id}", response_model=RestaurantSectorResponse)
async def update_sector(
    sector_id: UUID,
    payload: RestaurantSectorRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await UpdateRestaurantSector(
            SQLAlchemyRestaurantSectorRepository(session),
            SQLAlchemyRestaurantFloorRepository(session),
        ).execute(sector_id, _sector_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.sector.updated",
            action="updated",
            item=item,
            entity_type="restaurant_sector",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_SECTOR_UPDATED", data=_sector_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.delete("/sectors/{sector_id}", response_model=RestaurantSectorResponse)
async def delete_sector(
    sector_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await DeleteRestaurantSector(SQLAlchemyRestaurantSectorRepository(session)).execute(
            sector_id, tenant_id=user.tenant_id, actor_id=user.id
        )
        await _audit(
            session,
            event_name="restaurant.sector.deleted",
            action="deleted",
            item=item,
            entity_type="restaurant_sector",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_SECTOR_DELETED", data=_sector_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.get("/floors", response_model=list[RestaurantFloorResponse])
async def list_floors(
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
    is_active: bool | None = Query(default=None),
) -> JSONResponse:
    items = await ListRestaurantFloors(SQLAlchemyRestaurantFloorRepository(session)).execute(
        tenant_id=user.tenant_id, branch_id=user.branch_id, is_active=is_active
    )
    return success_response(
        "RESTAURANT_FLOOR_LIST_RETRIEVED",
        data=[_floor_response(item).model_dump(mode="json") for item in items],
    )


@router.get("/floors/{floor_id}", response_model=RestaurantFloorResponse)
async def get_floor(
    floor_id: UUID, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await GetRestaurantFloor(SQLAlchemyRestaurantFloorRepository(session)).execute(
            floor_id, tenant_id=user.tenant_id
        )
        return success_response(
            "RESTAURANT_FLOOR_RETRIEVED", data=_floor_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        return _error(exc)


@router.post("/floors", response_model=RestaurantFloorResponse)
async def create_floor(
    payload: RestaurantFloorRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await CreateRestaurantFloor(SQLAlchemyRestaurantFloorRepository(session)).execute(
            _floor_input(payload, user)
        )
        await _audit(
            session,
            event_name="restaurant.floor.created",
            action="created",
            item=item,
            entity_type="restaurant_floor",
            user=user,
            request=request,
        )
        await session.commit()
        logger.info("restaurant.floor.created", extra={"event": "restaurant.floor.created"})
        return success_response(
            "RESTAURANT_FLOOR_CREATED", data=_floor_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.put("/floors/{floor_id}", response_model=RestaurantFloorResponse)
async def update_floor(
    floor_id: UUID,
    payload: RestaurantFloorRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await UpdateRestaurantFloor(SQLAlchemyRestaurantFloorRepository(session)).execute(
            floor_id, _floor_input(payload, user)
        )
        await _audit(
            session,
            event_name="restaurant.floor.updated",
            action="updated",
            item=item,
            entity_type="restaurant_floor",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_FLOOR_UPDATED", data=_floor_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.delete("/floors/{floor_id}", response_model=RestaurantFloorResponse)
async def delete_floor(
    floor_id: UUID, request: Request, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await DeleteRestaurantFloor(SQLAlchemyRestaurantFloorRepository(session)).execute(
            floor_id, tenant_id=user.tenant_id, actor_id=user.id
        )
        await _audit(
            session,
            event_name="restaurant.floor.deleted",
            action="deleted",
            item=item,
            entity_type="restaurant_floor",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_FLOOR_DELETED", data=_floor_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.get("/tables", response_model=list[RestaurantTableResponse])
async def list_tables(
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
    floor_id: Annotated[UUID | None, Query()] = None,
    is_active: Annotated[bool | None, Query()] = None,
) -> JSONResponse:
    items = await ListRestaurantTables(SQLAlchemyRestaurantTableRepository(session)).execute(
        tenant_id=user.tenant_id, branch_id=user.branch_id, floor_id=floor_id, is_active=is_active
    )
    return success_response(
        "RESTAURANT_TABLE_LIST_RETRIEVED",
        data=[_table_response(item).model_dump(mode="json") for item in items],
    )


@router.get("/tables/{table_id}", response_model=RestaurantTableResponse)
async def get_table(
    table_id: UUID, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await GetRestaurantTable(SQLAlchemyRestaurantTableRepository(session)).execute(
            table_id, tenant_id=user.tenant_id
        )
        return success_response(
            "RESTAURANT_TABLE_RETRIEVED", data=_table_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        return _error(exc)


@router.post("/tables", response_model=RestaurantTableResponse)
async def create_table(
    payload: RestaurantTableRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await CreateRestaurantTable(
            SQLAlchemyRestaurantFloorRepository(session),
            SQLAlchemyRestaurantTableRepository(session),
        ).execute(_table_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.table.created",
            action="created",
            item=item,
            entity_type="restaurant_table",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_TABLE_CREATED", data=_table_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.put("/tables/{table_id}", response_model=RestaurantTableResponse)
async def update_table(
    table_id: UUID,
    payload: RestaurantTableRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await UpdateRestaurantTable(
            SQLAlchemyRestaurantFloorRepository(session),
            SQLAlchemyRestaurantTableRepository(session),
        ).execute(table_id, _table_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.table.updated",
            action="updated",
            item=item,
            entity_type="restaurant_table",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_TABLE_UPDATED", data=_table_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.delete("/tables/{table_id}", response_model=RestaurantTableResponse)
async def delete_table(
    table_id: UUID, request: Request, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await DeleteRestaurantTable(SQLAlchemyRestaurantTableRepository(session)).execute(
            table_id, tenant_id=user.tenant_id, actor_id=user.id
        )
        await _audit(
            session,
            event_name="restaurant.table.deleted",
            action="deleted",
            item=item,
            entity_type="restaurant_table",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_TABLE_DELETED", data=_table_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


def _error(exc: RestaurantError) -> JSONResponse:
    if isinstance(exc, RestaurantSectorNotFoundError):
        return error_response("RESTAURANT_SECTOR_NOT_FOUND")
    if isinstance(exc, RestaurantFloorNotFoundError):
        return error_response("RESTAURANT_FLOOR_NOT_FOUND")
    if isinstance(exc, RestaurantTableNotFoundError):
        return error_response("RESTAURANT_TABLE_NOT_FOUND")
    if isinstance(exc, RestaurantFloorCodeAlreadyExistsError):
        return error_response("RESTAURANT_FLOOR_CODE_ALREADY_EXISTS")
    if isinstance(exc, RestaurantSectorCodeAlreadyExistsError):
        return error_response("RESTAURANT_SECTOR_CODE_ALREADY_EXISTS")
    if isinstance(exc, RestaurantTableNumberAlreadyExistsError):
        return error_response("RESTAURANT_TABLE_NUMBER_ALREADY_EXISTS")
    if isinstance(exc, RestaurantBranchRequiredError):
        return error_response("RESTAURANT_BRANCH_REQUIRED")
    if isinstance(exc, RestaurantInvalidDataError):
        return error_response("RESTAURANT_INVALID_DATA")
    return error_response("INTERNAL_SERVER_ERROR")
