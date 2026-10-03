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
from app.modules.inventory.application.inventory_count_service import (
    InventoryCountCreateInput,
    InventoryCountError,
    InventoryCountService,
)
from app.modules.inventory.application.inventory_transfer_service import (
    InventoryTransferCreateInput,
    InventoryTransferService,
)
from app.modules.inventory.application.putaway_service import PutAwayInput, PutAwayService
from app.modules.inventory.application.use_cases import (
    CreateInventoryAdjustment,
    CreateInventoryReservation,
    GetInventoryTransaction,
    InventoryAdjustmentInput,
    InventoryListInput,
    InventoryReservationInput,
    ListInventoryBalances,
    ListInventoryMovements,
    ListInventoryTransactions,
    ReleaseInventoryReservation,
    ReverseInventoryAdjustment,
)
from app.modules.inventory.domain.entities import (
    InventoryCountStatus,
    InventoryMovementType,
    InventoryTransferStatus,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBalanceNotFoundError,
    InventoryBranchRequiredError,
    InventoryError,
    InventoryInsufficientStockError,
    InventoryInvalidQuantityError,
    InventoryMovementNotFoundError,
    InventoryProductNotFoundError,
    InventoryReservationInactiveError,
    InventoryReservationNotFoundError,
    InventoryTransferError,
    InventoryWarehouseNotFoundError,
    PutAwayCannotConfirmError,
    ReceivingDocumentNotFoundError,
    WarehouseLocationBranchRequiredError,
    WarehouseLocationNotFoundError,
)
from app.modules.inventory.infrastructure.count_repositories import (
    SQLAlchemyInventoryCountRepository,
)
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryCountModel,
    InventoryMovementModel,
    InventoryReservationModel,
    InventoryTransferModel,
)
from app.modules.inventory.infrastructure.receiving_repositories import (
    SQLAlchemyReceivingDocumentRepository,
)
from app.modules.inventory.infrastructure.repositories import SQLAlchemyInventoryRepository
from app.modules.inventory.infrastructure.transfer_repositories import (
    SQLAlchemyInventoryTransferRepository,
)
from app.modules.inventory.infrastructure.warehouse_location_repositories import (
    SQLAlchemyWarehouseLocationRepository,
)
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.inventory.presentation.schemas import (
    InventoryAdjustmentRequest,
    InventoryAdjustmentResponse,
    InventoryAdjustmentReverseRequest,
    InventoryBalanceResponse,
    InventoryCountCreateRequest,
    InventoryCountItemQuantityRequest,
    InventoryCountItemResponse,
    InventoryCountResponse,
    InventoryMovementResponse,
    InventoryOperationResponse,
    InventoryReservationRequest,
    InventoryReservationResponse,
    InventoryTransferCreateRequest,
    InventoryTransferResponse,
    PutAwayConfirmRequest,
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
        putaway_pending_quantity=balance.putaway_pending_quantity,
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
        putaway_pending_quantity_delta=movement.putaway_pending_quantity_delta,
        reason=movement.reason,
        source_module=movement.source_module,
        source_id=movement.source_id,
        origin_module=movement.origin_module,
        business_process=movement.business_process,
        event_name=movement.event_name,
        actor_id=movement.actor_id,
        immutable=True,
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
        reason_code=adjustment.reason_code,
        reversal_of_id=adjustment.reversal_of_id,
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


def _count_response(count: InventoryCountModel) -> InventoryCountResponse:
    return InventoryCountResponse(
        id=count.id,
        tenant_id=count.tenant_id,
        branch_id=count.branch_id,
        warehouse_id=count.warehouse_id,
        location_id=count.location_id,
        code=count.code,
        status=count.status,
        notes=count.notes,
        started_at=count.started_at,
        finished_at=count.finished_at,
        created_at=count.created_at,
        updated_at=count.updated_at,
        items=[
            InventoryCountItemResponse(
                id=item.id,
                product_id=item.product_id,
                expected_quantity=item.expected_quantity,
                counted_quantity=item.counted_quantity,
                divergence_quantity=(item.counted_quantity - item.expected_quantity)
                if item.counted_quantity is not None
                else None,
                adjustment_movement_id=item.adjustment_movement_id,
            )
            for item in count.items
        ],
    )


def _count_service(session: AsyncSession) -> InventoryCountService:
    return InventoryCountService(
        SQLAlchemyInventoryCountRepository(session),
        SQLAlchemyInventoryRepository(session),
        SQLAlchemyProductRepository(session),
    )


def _transfer_response(transfer: InventoryTransferModel) -> InventoryTransferResponse:
    return InventoryTransferResponse(
        id=transfer.id,
        tenant_id=transfer.tenant_id,
        code=transfer.code,
        product_id=transfer.product_id,
        source_branch_id=transfer.source_branch_id,
        source_warehouse_id=transfer.source_warehouse_id,
        source_location_id=transfer.source_location_id,
        target_branch_id=transfer.target_branch_id,
        target_warehouse_id=transfer.target_warehouse_id,
        target_location_id=transfer.target_location_id,
        quantity=transfer.quantity,
        status=transfer.status,
        reason=transfer.reason,
        notes=transfer.notes,
        outbound_movement_id=transfer.outbound_movement_id,
        inbound_movement_id=transfer.inbound_movement_id,
        dispatched_at=transfer.dispatched_at,
        received_at=transfer.received_at,
        cancelled_at=transfer.cancelled_at,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at,
    )


def _transfer_service(session: AsyncSession) -> InventoryTransferService:
    return InventoryTransferService(
        SQLAlchemyInventoryTransferRepository(session),
        SQLAlchemyInventoryRepository(session),
        SQLAlchemyProductRepository(session),
        SQLAlchemyWarehouseRepository(session),
        SQLAlchemyWarehouseLocationRepository(session),
    )


def _putaway_response(result) -> dict[str, object]:
    return {
        "document_id": str(result.document.id),
        "document_status": result.document.status.value,
        "source_balance": _balance_response(result.source_balance).model_dump(mode="json"),
        "target_balance": _balance_response(result.target_balance).model_dump(mode="json"),
        "movement": _movement_response(result.movement).model_dump(mode="json"),
    }


def _snapshot(balance: InventoryBalanceModel) -> dict[str, str]:
    return {
        "id": str(balance.id),
        "tenant_id": str(balance.tenant_id),
        "branch_id": str(balance.branch_id),
        "product_id": str(balance.product_id),
        "physical_quantity": str(balance.physical_quantity),
        "reserved_quantity": str(balance.reserved_quantity),
        "putaway_pending_quantity": str(balance.putaway_pending_quantity),
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


@router.get("/transactions", response_model=list[InventoryMovementResponse])
async def list_inventory_transactions(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    branch_id: OptionalUUIDQuery = None,
    product_id: OptionalUUIDQuery = None,
    warehouse_id: OptionalUUIDQuery = None,
    location_id: OptionalUUIDQuery = None,
    movement_type: Annotated[InventoryMovementType | None, Query()] = None,
    origin_module: Annotated[str | None, Query(max_length=80)] = None,
    business_process: Annotated[str | None, Query(max_length=80)] = None,
    source_module: Annotated[str | None, Query(max_length=80)] = None,
) -> JSONResponse:
    result = await ListInventoryTransactions(SQLAlchemyInventoryRepository(session)).execute(
        InventoryListInput(
            tenant_id=current_user.tenant_id,
            branch_id=branch_id or current_user.branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            movement_type=movement_type,
            origin_module=origin_module,
            business_process=business_process,
            source_module=source_module,
            page=page,
            page_size=page_size,
        )
    )
    return success_response(
        "INVENTORY_TRANSACTION_LIST_RETRIEVED",
        data=[_movement_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/transactions/{transaction_id}", response_model=InventoryMovementResponse)
async def get_inventory_transaction(
    transaction_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        movement = await GetInventoryTransaction(SQLAlchemyInventoryRepository(session)).execute(
            transaction_id,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
        )
        return success_response(
            "INVENTORY_TRANSACTION_RETRIEVED",
            data=_movement_response(movement).model_dump(mode="json"),
        )
    except InventoryError as exc:
        return inventory_exception_to_response(exc)


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
            SQLAlchemyWarehouseRepository(session),
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
                reason_code=payload.reason_code,
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


@router.post("/adjustments/{adjustment_id}/reverse", response_model=InventoryOperationResponse)
async def reverse_inventory_adjustment(
    adjustment_id: UUID,
    payload: InventoryAdjustmentReverseRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        result = await ReverseInventoryAdjustment(
            SQLAlchemyInventoryRepository(session),
            SQLAlchemyProductRepository(session),
            SQLAlchemyWarehouseRepository(session),
        ).execute(
            adjustment_id,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            reason=payload.reason,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.adjustment.reversed",
            action="reversed",
            entity_type="inventory_adjustment",
            entity_id=result.adjustment.id if result.adjustment else adjustment_id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data=_snapshot(result.balance),
        )
        await session.commit()
        return success_response(
            "INVENTORY_ADJUSTMENT_REVERSED",
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
            SQLAlchemyWarehouseRepository(session),
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


@router.get("/counts", response_model=list[InventoryCountResponse])
async def list_inventory_counts(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    branch_id: OptionalUUIDQuery = None,
    status: Annotated[InventoryCountStatus | None, Query()] = None,
) -> JSONResponse:
    repository = SQLAlchemyInventoryCountRepository(session)
    active_branch = branch_id or current_user.branch_id
    items = await repository.list(
        tenant_id=current_user.tenant_id,
        branch_id=active_branch,
        status=status,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    total = await repository.count(
        tenant_id=current_user.tenant_id, branch_id=active_branch, status=status
    )
    return success_response(
        "INVENTORY_COUNT_LIST_RETRIEVED",
        data=[_count_response(item).model_dump(mode="json") for item in items],
        meta=PaginationMeta.from_total(page=page, page_size=page_size, total=total),
    )


@router.post("/counts", response_model=InventoryCountResponse)
async def create_inventory_count(
    payload: InventoryCountCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        count = await _count_service(session).create(
            InventoryCountCreateInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                warehouse_id=payload.warehouse_id,
                location_id=payload.location_id,
                code=payload.code,
                product_ids=payload.product_ids,
                notes=payload.notes,
                actor_id=current_user.id,
            )
        )
        await _record_inventory_event(
            session,
            event_name="inventory.count.created",
            action="created",
            entity_type="inventory_count",
            entity_id=count.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={"code": count.code, "status": count.status.value},
        )
        await session.commit()
        return success_response(
            "INVENTORY_COUNT_CREATED", data=_count_response(count).model_dump(mode="json")
        )
    except (InventoryError, InventoryCountError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/counts/{count_id}/start", response_model=InventoryCountResponse)
async def start_inventory_count(
    count_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        count = await _count_service(session).start(
            count_id,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.count.started",
            action="started",
            entity_type="inventory_count",
            entity_id=count.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
        )
        await session.commit()
        return success_response(
            "INVENTORY_COUNT_STARTED", data=_count_response(count).model_dump(mode="json")
        )
    except (InventoryError, InventoryCountError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.put("/counts/{count_id}/items/{item_id}", response_model=InventoryCountResponse)
async def record_inventory_count_item(
    count_id: UUID,
    item_id: UUID,
    payload: InventoryCountItemQuantityRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        count = await _count_service(session).record_item(
            count_id,
            item_id,
            payload.counted_quantity,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.count.item_recorded",
            action="item_recorded",
            entity_type="inventory_count",
            entity_id=count.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
        )
        await session.commit()
        return success_response(
            "INVENTORY_COUNT_ITEM_RECORDED", data=_count_response(count).model_dump(mode="json")
        )
    except (InventoryError, InventoryCountError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/counts/{count_id}/finish", response_model=InventoryCountResponse)
async def finish_inventory_count(
    count_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        count = await _count_service(session).finish(
            count_id,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.count.finished",
            action="finished",
            entity_type="inventory_count",
            entity_id=count.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
        )
        await session.commit()
        return success_response(
            "INVENTORY_COUNT_FINISHED", data=_count_response(count).model_dump(mode="json")
        )
    except (InventoryError, InventoryCountError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/counts/{count_id}/cancel", response_model=InventoryCountResponse)
async def cancel_inventory_count(
    count_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        count = await _count_service(session).cancel(
            count_id,
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.count.cancelled",
            action="cancelled",
            entity_type="inventory_count",
            entity_id=count.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
        )
        await session.commit()
        return success_response(
            "INVENTORY_COUNT_CANCELLED", data=_count_response(count).model_dump(mode="json")
        )
    except (InventoryError, InventoryCountError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.get("/transfers", response_model=list[InventoryTransferResponse])
async def list_inventory_transfers(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    status: Annotated[InventoryTransferStatus | None, Query()] = None,
) -> JSONResponse:
    repository = SQLAlchemyInventoryTransferRepository(session)
    items = await repository.list(
        tenant_id=current_user.tenant_id,
        branch_id=current_user.branch_id,
        status=status,
        limit=page_size,
        offset=(page - 1) * page_size,
    )
    total = await repository.count(
        tenant_id=current_user.tenant_id, branch_id=current_user.branch_id, status=status
    )
    return success_response(
        "INVENTORY_TRANSFER_LIST_RETRIEVED",
        data=[_transfer_response(item).model_dump(mode="json") for item in items],
        meta=PaginationMeta.from_total(page=page, page_size=page_size, total=total),
    )


@router.post("/transfers", response_model=InventoryTransferResponse)
async def create_inventory_transfer(
    payload: InventoryTransferCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        transfer = await _transfer_service(session).create(
            InventoryTransferCreateInput(
                tenant_id=current_user.tenant_id,
                source_branch_id=current_user.branch_id,
                source_warehouse_id=payload.source_warehouse_id,
                source_location_id=payload.source_location_id,
                target_branch_id=payload.target_branch_id,
                target_warehouse_id=payload.target_warehouse_id,
                target_location_id=payload.target_location_id,
                product_id=payload.product_id,
                quantity=payload.quantity,
                code=payload.code,
                reason=payload.reason,
                notes=payload.notes,
                actor_id=current_user.id,
            )
        )
        await _record_inventory_event(
            session,
            event_name="inventory.transfer.requested",
            action="requested",
            entity_type="inventory_transfer",
            entity_id=transfer.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={"code": transfer.code, "status": transfer.status.value},
        )
        await session.commit()
        return success_response(
            "INVENTORY_TRANSFER_CREATED", data=_transfer_response(transfer).model_dump(mode="json")
        )
    except (InventoryError, InventoryTransferError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/transfers/{transfer_id}/dispatch", response_model=InventoryTransferResponse)
async def dispatch_inventory_transfer(
    transfer_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        transfer = await _transfer_service(session).dispatch(
            transfer_id,
            tenant_id=current_user.tenant_id,
            active_branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.transfer.dispatched",
            action="dispatched",
            entity_type="inventory_transfer",
            entity_id=transfer.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={
                "status": transfer.status.value,
                "movement_id": str(transfer.outbound_movement_id),
            },
        )
        await session.commit()
        return success_response(
            "INVENTORY_TRANSFER_DISPATCHED",
            data=_transfer_response(transfer).model_dump(mode="json"),
        )
    except (InventoryError, InventoryTransferError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/transfers/{transfer_id}/receive", response_model=InventoryTransferResponse)
async def receive_inventory_transfer(
    transfer_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        transfer = await _transfer_service(session).receive(
            transfer_id,
            tenant_id=current_user.tenant_id,
            active_branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.transfer.received",
            action="received",
            entity_type="inventory_transfer",
            entity_id=transfer.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={
                "status": transfer.status.value,
                "movement_id": str(transfer.inbound_movement_id),
            },
        )
        await session.commit()
        return success_response(
            "INVENTORY_TRANSFER_RECEIVED", data=_transfer_response(transfer).model_dump(mode="json")
        )
    except (InventoryError, InventoryTransferError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/transfers/{transfer_id}/cancel", response_model=InventoryTransferResponse)
async def cancel_inventory_transfer(
    transfer_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        transfer = await _transfer_service(session).cancel(
            transfer_id,
            tenant_id=current_user.tenant_id,
            active_branch_id=current_user.branch_id,
            actor_id=current_user.id,
        )
        await _record_inventory_event(
            session,
            event_name="inventory.transfer.cancelled",
            action="cancelled",
            entity_type="inventory_transfer",
            entity_id=transfer.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={"status": transfer.status.value},
        )
        await session.commit()
        return success_response(
            "INVENTORY_TRANSFER_CANCELLED",
            data=_transfer_response(transfer).model_dump(mode="json"),
        )
    except (InventoryError, InventoryTransferError) as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


@router.post("/putaway")
async def confirm_putaway(
    payload: PutAwayConfirmRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        service = PutAwayService(
            SQLAlchemyReceivingDocumentRepository(session),
            SQLAlchemyInventoryRepository(session),
            SQLAlchemyWarehouseLocationRepository(session),
        )
        result = await service.confirm(
            PutAwayInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                document_id=payload.document_id,
                product_id=payload.product_id,
                location_id=payload.location_id,
                quantity=payload.quantity,
                reason=payload.reason,
                actor_id=current_user.id,
            )
        )
        await _record_inventory_event(
            session,
            event_name=result.movement.event_name,
            action="putaway_confirmed",
            entity_type="inventory_movement",
            entity_id=result.movement.id,
            tenant_id=current_user.tenant_id,
            current_user=current_user,
            after_data={
                "source_balance": _snapshot(result.source_balance),
                "target_balance": _snapshot(result.target_balance),
            },
        )
        audit_logger.info(
            result.movement.event_name,
            extra={
                "event": result.movement.event_name,
                "tenant_id": str(current_user.tenant_id),
                "branch_id": str(result.movement.branch_id),
                "product_id": str(payload.product_id),
                "location_id": str(payload.location_id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "PUTAWAY_CONFIRMED",
            data=_putaway_response(result),
        )
    except InventoryError as exc:
        await session.rollback()
        return inventory_exception_to_response(exc)


def inventory_exception_to_response(
    exc: InventoryError | InventoryCountError | InventoryTransferError,
) -> JSONResponse:
    if isinstance(exc, InventoryCountError):
        return error_response("INVENTORY_COUNT_INVALID_STATE")
    if isinstance(exc, InventoryTransferError):
        return error_response("INVENTORY_TRANSFER_INVALID_STATE")
    if isinstance(exc, InventoryBranchRequiredError):
        return error_response("INVENTORY_BRANCH_REQUIRED")
    if isinstance(exc, InventoryProductNotFoundError):
        return error_response("PRODUCT_NOT_FOUND")
    if isinstance(exc, InventoryWarehouseNotFoundError):
        return error_response("WAREHOUSE_NOT_FOUND")
    if isinstance(exc, InventoryBalanceNotFoundError):
        return error_response("INVENTORY_BALANCE_NOT_FOUND")
    if isinstance(exc, InventoryMovementNotFoundError):
        return error_response("INVENTORY_TRANSACTION_NOT_FOUND")
    if isinstance(exc, InventoryInsufficientStockError):
        return error_response("INVENTORY_INSUFFICIENT_STOCK")
    if isinstance(exc, InventoryInvalidQuantityError):
        return error_response("INVENTORY_INVALID_QUANTITY")
    if isinstance(exc, InventoryReservationNotFoundError):
        return error_response("INVENTORY_RESERVATION_NOT_FOUND")
    if isinstance(exc, InventoryReservationInactiveError):
        return error_response("INVENTORY_RESERVATION_INACTIVE")
    if isinstance(exc, PutAwayCannotConfirmError):
        return error_response("PUTAWAY_CANNOT_CONFIRM")
    if isinstance(exc, ReceivingDocumentNotFoundError):
        return error_response("RECEIVING_DOCUMENT_NOT_FOUND")
    if isinstance(exc, WarehouseLocationNotFoundError):
        return error_response("WAREHOUSE_LOCATION_NOT_FOUND")
    if isinstance(exc, WarehouseLocationBranchRequiredError):
        return error_response("WAREHOUSE_LOCATION_BRANCH_REQUIRED")
    return error_response("INTERNAL_SERVER_ERROR")
