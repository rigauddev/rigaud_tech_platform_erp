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
from app.modules.inventory.application.warehouse_use_cases import (
    CreateWarehouse,
    DeleteWarehouse,
    GetWarehouse,
    ListWarehouses,
    SetDefaultWarehouse,
    UpdateWarehouse,
    WarehouseCreateInput,
    WarehouseListInput,
    WarehouseUpdateInput,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseCodeAlreadyExistsError,
    WarehouseError,
    WarehouseInvalidDataError,
    WarehouseNotFoundError,
)
from app.modules.inventory.infrastructure.models import WarehouseModel
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.inventory.presentation.warehouse_schemas import (
    WarehouseCreateRequest,
    WarehouseResponse,
    WarehouseUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
OptionalBoolQuery = Annotated[bool | None, Query()]


def _warehouse_response(warehouse: WarehouseModel) -> WarehouseResponse:
    return WarehouseResponse(
        id=warehouse.id,
        tenant_id=warehouse.tenant_id,
        branch_id=warehouse.branch_id,
        code=warehouse.code,
        name=warehouse.name,
        description=warehouse.description,
        address=warehouse.address,
        status=warehouse.status,
        is_default=warehouse.is_default,
        is_active=warehouse.is_active,
        created_at=warehouse.created_at,
        updated_at=warehouse.updated_at,
    )


def _snapshot(warehouse: WarehouseModel) -> dict[str, str | bool | None]:
    return {
        "id": str(warehouse.id),
        "tenant_id": str(warehouse.tenant_id),
        "branch_id": str(warehouse.branch_id),
        "code": warehouse.code,
        "name": warehouse.name,
        "description": warehouse.description,
        "address": warehouse.address,
        "status": warehouse.status.value,
        "is_default": warehouse.is_default,
        "is_active": warehouse.is_active,
    }


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _record_warehouse_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    warehouse: WarehouseModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="inventory",
            action=action,
            entity_type="warehouse",
            entity_id=warehouse.id,
            tenant_id=warehouse.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.get("", response_model=list[WarehouseResponse])
async def list_warehouses(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    is_active: OptionalBoolQuery = None,
) -> JSONResponse:
    result = await ListWarehouses(SQLAlchemyWarehouseRepository(session)).execute(
        WarehouseListInput(
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )
    )
    logger.info(
        "warehouse.query.completed",
        extra={"event": "warehouse.query.completed", "tenant_id": str(current_user.tenant_id)},
    )
    return success_response(
        "WAREHOUSE_LIST_RETRIEVED",
        data=[_warehouse_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{warehouse_id}", response_model=WarehouseResponse)
async def get_warehouse(
    warehouse_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        warehouse = await GetWarehouse(SQLAlchemyWarehouseRepository(session)).execute(
            warehouse_id,
            tenant_id=current_user.tenant_id,
        )
        return success_response(
            "WAREHOUSE_RETRIEVED",
            data=_warehouse_response(warehouse).model_dump(mode="json"),
        )
    except WarehouseError as exc:
        return warehouse_exception_to_response(exc)


@router.post("", response_model=WarehouseResponse)
async def create_warehouse(
    payload: WarehouseCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        warehouse = await CreateWarehouse(SQLAlchemyWarehouseRepository(session)).execute(
            WarehouseCreateInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                code=payload.code,
                name=payload.name,
                description=payload.description,
                address=payload.address,
                is_default=payload.is_default,
                is_active=payload.is_active,
                actor_id=current_user.id,
            )
        )
        await _record_warehouse_event(
            session,
            event_name="warehouse.created",
            action="created",
            warehouse=warehouse,
            current_user=current_user,
            after_data=_snapshot(warehouse),
        )
        audit_logger.info(
            "warehouse.created",
            extra={
                "event": "warehouse.created",
                "tenant_id": str(current_user.tenant_id),
                "warehouse_id": str(warehouse.id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_CREATED",
            data=_warehouse_response(warehouse).model_dump(mode="json"),
        )
    except WarehouseError as exc:
        await session.rollback()
        return warehouse_exception_to_response(exc)


@router.put("/{warehouse_id}", response_model=WarehouseResponse)
async def update_warehouse(
    warehouse_id: UUID,
    payload: WarehouseUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    repository = SQLAlchemyWarehouseRepository(session)
    try:
        current = await GetWarehouse(repository).execute(
            warehouse_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        warehouse = await UpdateWarehouse(repository).execute(
            warehouse_id,
            tenant_id=current_user.tenant_id,
            input_data=WarehouseUpdateInput(
                code=payload.code,
                name=payload.name,
                description=payload.description,
                address=payload.address,
                is_active=payload.is_active,
                is_default=payload.is_default,
                actor_id=current_user.id,
            ),
        )
        await _record_warehouse_event(
            session,
            event_name="warehouse.updated",
            action="updated",
            warehouse=warehouse,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(warehouse),
        )
        audit_logger.info(
            "warehouse.updated",
            extra={"event": "warehouse.updated", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_UPDATED",
            data=_warehouse_response(warehouse).model_dump(mode="json"),
        )
    except WarehouseError as exc:
        await session.rollback()
        return warehouse_exception_to_response(exc)


@router.post("/{warehouse_id}/default", response_model=WarehouseResponse)
async def set_default_warehouse(
    warehouse_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        warehouse = await SetDefaultWarehouse(SQLAlchemyWarehouseRepository(session)).execute(
            warehouse_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_warehouse_event(
            session,
            event_name="warehouse.default.changed",
            action="default_changed",
            warehouse=warehouse,
            current_user=current_user,
            after_data=_snapshot(warehouse),
        )
        audit_logger.info(
            "warehouse.default.changed",
            extra={"event": "warehouse.default.changed", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_DEFAULT_SET",
            data=_warehouse_response(warehouse).model_dump(mode="json"),
        )
    except WarehouseError as exc:
        await session.rollback()
        return warehouse_exception_to_response(exc)


@router.delete("/{warehouse_id}", response_model=WarehouseResponse)
async def delete_warehouse(
    warehouse_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        warehouse = await DeleteWarehouse(SQLAlchemyWarehouseRepository(session)).execute(
            warehouse_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_warehouse_event(
            session,
            event_name="warehouse.deleted",
            action="deleted",
            warehouse=warehouse,
            current_user=current_user,
            after_data=_snapshot(warehouse),
        )
        audit_logger.info(
            "warehouse.deleted",
            extra={"event": "warehouse.deleted", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "WAREHOUSE_DELETED",
            data=_warehouse_response(warehouse).model_dump(mode="json"),
        )
    except WarehouseError as exc:
        await session.rollback()
        return warehouse_exception_to_response(exc)


def warehouse_exception_to_response(exc: WarehouseError) -> JSONResponse:
    if isinstance(exc, WarehouseNotFoundError):
        return error_response("WAREHOUSE_NOT_FOUND")
    if isinstance(exc, WarehouseCodeAlreadyExistsError):
        return error_response("WAREHOUSE_CODE_ALREADY_EXISTS")
    if isinstance(exc, WarehouseBranchRequiredError):
        return error_response("WAREHOUSE_BRANCH_REQUIRED")
    if isinstance(exc, WarehouseInvalidDataError):
        return error_response("WAREHOUSE_INVALID_DATA")
    return error_response("INTERNAL_SERVER_ERROR")
