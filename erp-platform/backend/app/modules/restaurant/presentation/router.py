import logging
from datetime import date
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
from app.modules.restaurant.application.menu_availability_use_cases import (
    CreateRestaurantMenuAvailability,
    DeleteRestaurantMenuAvailability,
    GetRestaurantMenuAvailability,
    ListRestaurantMenuAvailabilities,
    MenuAvailabilityInput,
    UpdateRestaurantMenuAvailability,
)
from app.modules.restaurant.application.sector_use_cases import (
    CreateRestaurantSector,
    DeleteRestaurantSector,
    GetRestaurantSector,
    ListRestaurantSectors,
    SectorInput,
    UpdateRestaurantSector,
)
from app.modules.restaurant.application.staff_use_cases import (
    CreateRestaurantStaff,
    DeleteRestaurantStaff,
    GetRestaurantStaff,
    ListRestaurantStaff,
    StaffInput,
    UpdateRestaurantStaff,
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
    RestaurantMenuAvailabilityAlreadyExistsError,
    RestaurantMenuAvailabilityNotFoundError,
    RestaurantSectorCodeAlreadyExistsError,
    RestaurantSectorNotFoundError,
    RestaurantStaffCodeAlreadyExistsError,
    RestaurantStaffNotFoundError,
    RestaurantTableNotFoundError,
    RestaurantTableNumberAlreadyExistsError,
)
from app.modules.restaurant.infrastructure.models import (
    RestaurantFloorModel,
    RestaurantMenuAvailabilityModel,
    RestaurantSectorModel,
    RestaurantStaffModel,
    RestaurantTableModel,
)
from app.modules.restaurant.infrastructure.repositories import (
    SQLAlchemyRestaurantFloorRepository,
    SQLAlchemyRestaurantMenuAvailabilityRepository,
    SQLAlchemyRestaurantSectorRepository,
    SQLAlchemyRestaurantStaffRepository,
    SQLAlchemyRestaurantTableRepository,
)
from app.modules.restaurant.presentation.schemas import (
    RestaurantFloorRequest,
    RestaurantFloorResponse,
    RestaurantMenuAvailabilityRequest,
    RestaurantMenuAvailabilityResponse,
    RestaurantSectorRequest,
    RestaurantSectorResponse,
    RestaurantStaffRequest,
    RestaurantStaffResponse,
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


def _staff_response(item: RestaurantStaffModel) -> RestaurantStaffResponse:
    return RestaurantStaffResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        branch_id=item.branch_id,
        user_id=item.user_id,
        sector_id=item.sector_id,
        code=item.code,
        name=item.name,
        role=item.role,
        status=item.status,
        can_receive_online_orders=item.can_receive_online_orders,
        is_active=item.is_active,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _menu_availability_response(
    item: RestaurantMenuAvailabilityModel,
) -> RestaurantMenuAvailabilityResponse:
    return RestaurantMenuAvailabilityResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        branch_id=item.branch_id,
        product_id=item.product_id,
        service_date=item.service_date,
        service_period=item.service_period,
        channels=item.channels,
        available_quantity=item.available_quantity,
        sold_quantity=item.sold_quantity,
        status=item.status,
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


def _staff_input(payload: RestaurantStaffRequest, user: AuthenticatedUser) -> StaffInput:
    return StaffInput(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        code=payload.code,
        name=payload.name,
        role=payload.role,
        status=payload.status,
        sector_id=payload.sector_id,
        user_id=payload.user_id,
        can_receive_online_orders=payload.can_receive_online_orders,
        is_active=payload.is_active,
        actor_id=user.id,
    )


def _menu_availability_input(
    payload: RestaurantMenuAvailabilityRequest, user: AuthenticatedUser
) -> MenuAvailabilityInput:
    return MenuAvailabilityInput(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        product_id=payload.product_id,
        service_date=payload.service_date,
        service_period=payload.service_period,
        channels=payload.channels,
        available_quantity=payload.available_quantity,
        status=payload.status,
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
    item: RestaurantFloorModel
    | RestaurantSectorModel
    | RestaurantStaffModel
    | RestaurantMenuAvailabilityModel
    | RestaurantTableModel,
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


@router.get("/menu-availabilities", response_model=list[RestaurantMenuAvailabilityResponse])
async def list_menu_availabilities(
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
    service_date: Annotated[date | None, Query()] = None,
    service_period: Annotated[str | None, Query(max_length=40)] = None,
) -> JSONResponse:
    items = await ListRestaurantMenuAvailabilities(
        SQLAlchemyRestaurantMenuAvailabilityRepository(session)
    ).execute(
        tenant_id=user.tenant_id,
        branch_id=user.branch_id,
        service_date=service_date,
        service_period=service_period,
    )
    return success_response(
        "RESTAURANT_MENU_AVAILABILITY_LIST_RETRIEVED",
        data=[_menu_availability_response(item).model_dump(mode="json") for item in items],
    )


@router.get(
    "/menu-availabilities/{availability_id}", response_model=RestaurantMenuAvailabilityResponse
)
async def get_menu_availability(
    availability_id: UUID, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await GetRestaurantMenuAvailability(
            SQLAlchemyRestaurantMenuAvailabilityRepository(session)
        ).execute(availability_id, tenant_id=user.tenant_id)
        return success_response(
            "RESTAURANT_MENU_AVAILABILITY_RETRIEVED",
            data=_menu_availability_response(item).model_dump(mode="json"),
        )
    except RestaurantError as exc:
        return _error(exc)


@router.post("/menu-availabilities", response_model=RestaurantMenuAvailabilityResponse)
async def create_menu_availability(
    payload: RestaurantMenuAvailabilityRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await CreateRestaurantMenuAvailability(
            SQLAlchemyRestaurantMenuAvailabilityRepository(session)
        ).execute(_menu_availability_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.menu_availability.created",
            action="created",
            item=item,
            entity_type="restaurant_menu_availability",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_MENU_AVAILABILITY_CREATED",
            data=_menu_availability_response(item).model_dump(mode="json"),
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.put(
    "/menu-availabilities/{availability_id}", response_model=RestaurantMenuAvailabilityResponse
)
async def update_menu_availability(
    availability_id: UUID,
    payload: RestaurantMenuAvailabilityRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await UpdateRestaurantMenuAvailability(
            SQLAlchemyRestaurantMenuAvailabilityRepository(session)
        ).execute(availability_id, _menu_availability_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.menu_availability.updated",
            action="updated",
            item=item,
            entity_type="restaurant_menu_availability",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_MENU_AVAILABILITY_UPDATED",
            data=_menu_availability_response(item).model_dump(mode="json"),
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.delete(
    "/menu-availabilities/{availability_id}", response_model=RestaurantMenuAvailabilityResponse
)
async def delete_menu_availability(
    availability_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await DeleteRestaurantMenuAvailability(
            SQLAlchemyRestaurantMenuAvailabilityRepository(session)
        ).execute(availability_id, tenant_id=user.tenant_id, actor_id=user.id)
        await _audit(
            session,
            event_name="restaurant.menu_availability.deleted",
            action="deleted",
            item=item,
            entity_type="restaurant_menu_availability",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_MENU_AVAILABILITY_DELETED",
            data=_menu_availability_response(item).model_dump(mode="json"),
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.get("/staff", response_model=list[RestaurantStaffResponse])
async def list_staff(
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
    search: str | None = Query(default=None, max_length=120),
) -> JSONResponse:
    items = await ListRestaurantStaff(SQLAlchemyRestaurantStaffRepository(session)).execute(
        tenant_id=user.tenant_id, branch_id=user.branch_id, search=search
    )
    return success_response(
        "RESTAURANT_STAFF_LIST_RETRIEVED",
        data=[_staff_response(item).model_dump(mode="json") for item in items],
    )


@router.get("/staff/{staff_id}", response_model=RestaurantStaffResponse)
async def get_staff(
    staff_id: UUID, session: AsyncSessionDependency, user: CurrentUserDependency
) -> JSONResponse:
    try:
        item = await GetRestaurantStaff(SQLAlchemyRestaurantStaffRepository(session)).execute(
            staff_id, tenant_id=user.tenant_id
        )
        return success_response(
            "RESTAURANT_STAFF_RETRIEVED", data=_staff_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        return _error(exc)


@router.post("/staff", response_model=RestaurantStaffResponse)
async def create_staff(
    payload: RestaurantStaffRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await CreateRestaurantStaff(
            SQLAlchemyRestaurantStaffRepository(session),
            SQLAlchemyRestaurantSectorRepository(session),
        ).execute(_staff_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.staff.created",
            action="created",
            item=item,
            entity_type="restaurant_staff",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_STAFF_CREATED", data=_staff_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.put("/staff/{staff_id}", response_model=RestaurantStaffResponse)
async def update_staff(
    staff_id: UUID,
    payload: RestaurantStaffRequest,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await UpdateRestaurantStaff(
            SQLAlchemyRestaurantStaffRepository(session),
            SQLAlchemyRestaurantSectorRepository(session),
        ).execute(staff_id, _staff_input(payload, user))
        await _audit(
            session,
            event_name="restaurant.staff.updated",
            action="updated",
            item=item,
            entity_type="restaurant_staff",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_STAFF_UPDATED", data=_staff_response(item).model_dump(mode="json")
        )
    except RestaurantError as exc:
        await session.rollback()
        return _error(exc)


@router.delete("/staff/{staff_id}", response_model=RestaurantStaffResponse)
async def delete_staff(
    staff_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    user: CurrentUserDependency,
) -> JSONResponse:
    try:
        item = await DeleteRestaurantStaff(SQLAlchemyRestaurantStaffRepository(session)).execute(
            staff_id, tenant_id=user.tenant_id, actor_id=user.id
        )
        await _audit(
            session,
            event_name="restaurant.staff.deleted",
            action="deleted",
            item=item,
            entity_type="restaurant_staff",
            user=user,
            request=request,
        )
        await session.commit()
        return success_response(
            "RESTAURANT_STAFF_DELETED", data=_staff_response(item).model_dump(mode="json")
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
    if isinstance(exc, RestaurantMenuAvailabilityNotFoundError):
        return error_response("RESTAURANT_MENU_AVAILABILITY_NOT_FOUND")
    if isinstance(exc, RestaurantMenuAvailabilityAlreadyExistsError):
        return error_response("RESTAURANT_MENU_AVAILABILITY_ALREADY_EXISTS")
    if isinstance(exc, RestaurantStaffNotFoundError):
        return error_response("RESTAURANT_STAFF_NOT_FOUND")
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
    if isinstance(exc, RestaurantStaffCodeAlreadyExistsError):
        return error_response("RESTAURANT_STAFF_CODE_ALREADY_EXISTS")
    if isinstance(exc, RestaurantTableNumberAlreadyExistsError):
        return error_response("RESTAURANT_TABLE_NUMBER_ALREADY_EXISTS")
    if isinstance(exc, RestaurantBranchRequiredError):
        return error_response("RESTAURANT_BRANCH_REQUIRED")
    if isinstance(exc, RestaurantInvalidDataError):
        return error_response("RESTAURANT_INVALID_DATA")
    return error_response("INTERNAL_SERVER_ERROR")
