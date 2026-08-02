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
from app.modules.inventory.application.use_cases import (
    CreateInventoryAdjustment,
    CreateInventoryReservation,
    InventoryAdjustmentInput,
    InventoryListInput,
    InventoryReservationInput,
    ListInventoryBalances,
    ListInventoryMovements,
    ReleaseInventoryReservation,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBalanceNotFoundError,
    InventoryBranchRequiredError,
    InventoryError,
    InventoryInsufficientStockError,
    InventoryInvalidQuantityError,
    InventoryProductNotFoundError,
    InventoryReservationInactiveError,
    InventoryReservationNotFoundError,
)
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
)
from app.modules.inventory.infrastructure.repositories import SQLAlchemyInventoryRepository
from app.modules.inventory.presentation.schemas import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentResponse,
    InventoryBalanceResponse,
    InventoryMovementResponse,
    InventoryOperationResponse,
    InventoryReservationRequest,
    InventoryReservationResponse,
)
from app.modules.products.infrastructure.repositories import SQLAlchemyProductRepository
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/inventory", tags=["Inventory"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
OptionalUUIDQuery = Annotated[UUID | None, Query()]


def _balance_response(balance: InventoryBalanceModel) -> InventoryBalanceResponse:
    return InventoryBalanceResponse(
        id=balance.id,
        tenant_id=balance.tenant_id,
        branch_id=balance.branch_id,
        product_id=balance.product_id,
        warehouse_id=balance.warehouse_id,
        location_id=balance.location_id,
        physical_quantity=balance.physical_quantity,
        reserved_quantity=balance.reserved_quantity,
        available_quantity=balance.available_quantity,
        created_at=balance.created_at,
        updated_at=balance.updated_at,
    )


def _movement_response(movement: InventoryMovementModel) -> InventoryMovementResponse:
    return InventoryMovementResponse(
        id=movement.id,
        tenant_id=movement.tenant_id,
        branch_id=movement.branch_id,
        product_id=movement.product_id,
        warehouse_id=movement.warehouse_id,
        location_id=movement.location_id,
        movement_type=movement.movement_type,
        status=movement.status,
        physical_quantity_delta=movement.physical_quantity_delta,
        reserved_quantity_delta=movement.reserved_quantity_delta,
        reason=movement.reason,
        source_module=movement.source_module,
        source_id=movement.source_id,
        event_name=movement.event_name,
        actor_id=movement.actor_id,
        created_at=movement.created_at,
        updated_at=movement.updated_at,
    )


def _adjustment_response(adjustment: InventoryAdjustmentModel) -> InventoryAdjustmentResponse:
    return InventoryAdjustmentResponse(
        id=adjustment.id,
        tenant_id=adjustment.tenant_id,
        branch_id=adjustment.branch_id,
        product_id=adjustment.product_id,
        movement_id=adjustment.movement_id,
        warehouse_id=adjustment.warehouse_id,
        location_id=adjustment.location_id,
        adjustment_type=adjustment.adjustment_type,
        status=adjustment.status,
        quantity=adjustment.quantity,
        reason=adjustment.reason,
        notes=adjustment.notes,
        created_at=adjustment.created_at,
        updated_at=adjustment.updated_at,
    )


def _reservation_response(reservation: InventoryReservationModel) -> InventoryReservationResponse:
    return InventoryReservationResponse(
        id=reservation.id,
        tenant_id=reservation.tenant_id,
        branch_id=reservation.branch_id,
        product_id=reservation.product_id,
        warehouse_id=reservation.warehouse_id,
        location_id=reservation.location_id,
        status=reservation.status,
        quantity=reservation.quantity,
        reason=reservation.reason,
        source_module=reservation.source_module,
        source_id=reservation.source_id,
        created_at=reservation.created_at,
        updated_at=reservation.updated_at,
    )


def _operation_response(result) -> InventoryOperationResponse:
    return InventoryOperationResponse(
        balance=_balance_response(result.balance),
        movement=_movement_response(result.movement),
        adjustment=_adjustment_response(result.adjustment) if result.adjustment else None,
        reservation=_reservation_response(result.reservation) if result.reservation else None,
    )


def _snapshot(balance: InventoryBalanceModel) -> dict[str, str]:
    return {
        "id": str(balance.id),
        "tenant_id": str(balance.tenant_id),
        "branch_id": str(balance.branch_id),
        "product_id": str(balance.product_id),
        "physical_quantity": str(balance.physical_quantity),
        "reserved_quantity": str(balance.reserved_quantity),
        "available_quantity": str(balance.available_quantity),
    }


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _record_inventory_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    entity_id: UUID,
    entity_type: str,
    tenant_id: UUID,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="inventory",
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            tenant_id=tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.get("/balances", response_model=list[InventoryBalanceResponse])
async def list_inventory_balances(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    branch_id: OptionalUUIDQuery = None,
    product_id: OptionalUUIDQuery = None,
) -> JSONResponse:
    result = await ListInventoryBalances(SQLAlchemyInventoryRepository(session)).execute(
        InventoryListInput(
            tenant_id=current_user.tenant_id,
            branch_id=branch_id or current_user.branch_id,
            product_id=product_id,
            page=page,
            page_size=page_size,
        )
    )
    logger.info(
        "inventory.balance.query.completed",
        extra={
            "event": "inventory.balance.query.completed",
            "tenant_id": str(current_user.tenant_id),
        },
    )
    return success_response(
        "INVENTORY_BALANCE_LIST_RETRIEVED",
        data=[_balance_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/movements", response_model=list[InventoryMovementResponse])
async def list_inventory_movements(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    branch_id: OptionalUUIDQuery = None,
    product_id: OptionalUUIDQuery = None,
) -> JSONResponse:
    result = await ListInventoryMovements(SQLAlchemyInventoryRepository(session)).execute(
        InventoryListInput(
            tenant_id=current_user.tenant_id,
            branch_id=branch_id or current_user.branch_id,
            product_id=product_id,
            page=page,
            page_size=page_size,
        )
    )
    return success_response(
        "INVENTORY_MOVEMENT_LIST_RETRIEVED",
        data=[_movement_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.post("/adjustments", response_model=InventoryOperationResponse)
async def create_inventory_adjustment(
    payload: InventoryAdjustmentRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    inventory_repository = SQLAlchemyInventoryRepository(session)
    try:
        previous = (
            await inventory_repository.get_balance(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                product_id=payload.product_id,
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
            )
            if current_user.branch_id
            else None
        )
        before = _snapshot(previous) if previous else None
        result = await CreateInventoryAdjustment(
            inventory_repository,
            SQLAlchemyProductRepository(session),
        ).execute(
            InventoryAdjustmentInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                product_id=payload.product_id,
                adjustment_type=payload.adjustment_type,
                quantity=payload.quantity,
                reason=payload.reason,
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                notes=payload.notes,
                actor_id=current_user.id,
            )
        )
        await _record_inventory_event(
            session,
            event_name=result.movement.event_name,
            action="adjusted",
            entity_type="inventory_balance",
            entity_id=result.balance.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(result.balance),
        )
        audit_logger.info(
            result.movement.event_name,
            extra={
                "event": result.movement.event_name,
                "tenant_id": str(current_user.tenant_id),
                "branch_id": str(result.balance.branch_id),
                "product_id": str(payload.product_id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "INVENTORY_ADJUSTMENT_CREATED",
            data=_operation_response(result).model_dump(mode="json"),
        )
    except InventoryError as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/reservations", response_model=InventoryOperationResponse)
async def create_inventory_reservation(
    payload: InventoryReservationRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    inventory_repository = SQLAlchemyInventoryRepository(session)
    try:
        previous = (
            await inventory_repository.get_balance(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                product_id=payload.product_id,
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
            )
            if current_user.branch_id
            else None
        )
        before = _snapshot(previous) if previous else None
        result = await CreateInventoryReservation(
            inventory_repository,
            SQLAlchemyProductRepository(session),
        ).execute(
            InventoryReservationInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                product_id=payload.product_id,
                quantity=payload.quantity,
                reason=payload.reason,
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                source_module=payload.source_module,
                source_id=payload.source_id,
                actor_id=current_user.id,
            )
        )
        await _record_inventory_event(
            session,
            event_name="inventory.reserved",
            action="reserved",
            entity_type="inventory_reservation",
            entity_id=result.reservation.id if result.reservation else result.balance.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(result.balance),
        )
        audit_logger.info(
            "inventory.reserved",
            extra={
                "event": "inventory.reserved",
                "tenant_id": str(current_user.tenant_id),
                "branch_id": str(result.balance.branch_id),
                "product_id": str(payload.product_id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "INVENTORY_RESERVATION_CREATED",
            data=_operation_response(result).model_dump(mode="json"),
        )
    except InventoryError as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/reservations/{reservation_id}/release", response_model=InventoryOperationResponse)
async def release_inventory_reservation(
    reservation_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        result = await ReleaseInventoryReservation(SQLAlchemyInventoryRepository(session)).execute(
            reservation_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.reservation.released",
            action="reservation_released",
            entity_type="inventory_reservation",
            entity_id=reservation_id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data=_snapshot(result.balance),
        )
        audit_logger.info(
            "inventory.reservation.released",
            extra={"event": "inventory.reservation.released", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "INVENTORY_RESERVATION_RELEASED",
            data=_operation_response(result).model_dump(mode="json"),
        )
    except InventoryError as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


def inventory_exception_to_response(exc: InventoryError) -> JSONResponse:
    if isinstance(exc, InventoryBranchRequiredError):
        return error_response("INVENTORY_BRANCH_REQUIRED")
    if isinstance(exc, InventoryProductNotFoundError):
        return error_response("PRODUCT_NOT_FOUND")
    if isinstance(exc, InventoryBalanceNotFoundError):
        return error_response("INVENTORY_BALANCE_NOT_FOUND")
    if isinstance(exc, InventoryInsufficientStockError):
        return error_response("INVENTORY_INSUFFICIENT_STOCK")
    if isinstance(exc, InventoryInvalidQuantityError):
        return error_response("INVENTORY_INVALID_QUANTITY")
    if isinstance(exc, InventoryReservationNotFoundError):
        return error_response("INVENTORY_RESERVATION_NOT_FOUND")
    if isinstance(exc, InventoryReservationInactiveError):
        return error_response("INVENTORY_RESERVATION_INACTIVE")
    return error_response("INTERNAL_SERVER_ERROR")
