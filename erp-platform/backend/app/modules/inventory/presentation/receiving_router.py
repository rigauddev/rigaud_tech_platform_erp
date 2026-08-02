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
from app.modules.inventory.application.receiving_use_cases import (
    ChangeReceivingDocumentStatus,
    CreateReceivingDocument,
    DeleteReceivingDocument,
    GetReceivingDocument,
    ListReceivingDocuments,
    ReceivingDocumentCreateInput,
    ReceivingDocumentListInput,
    ReceivingDocumentStatusInput,
    ReceivingDocumentUpdateInput,
    ReceivingItemInput,
    UpdateReceivingDocument,
)
from app.modules.inventory.domain.entities import ReceivingDocumentStatus
from app.modules.inventory.domain.exceptions import (
    InventoryProductNotFoundError,
    ReceivingDocumentBranchRequiredError,
    ReceivingDocumentError,
    ReceivingDocumentInvalidDataError,
    ReceivingDocumentItemRequiredError,
    ReceivingDocumentNotFoundError,
    ReceivingDocumentNumberAlreadyExistsError,
    WarehouseBranchRequiredError,
    WarehouseError,
    WarehouseInactiveError,
    WarehouseNotFoundError,
)
from app.modules.inventory.infrastructure.models import (
    ReceivingDocumentModel,
    ReceivingItemModel,
)
from app.modules.inventory.infrastructure.receiving_repositories import (
    SQLAlchemyReceivingDocumentRepository,
)
from app.modules.inventory.infrastructure.warehouse_repositories import (
    SQLAlchemyWarehouseRepository,
)
from app.modules.inventory.presentation.receiving_schemas import (
    ReceivingDocumentCreateRequest,
    ReceivingDocumentResponse,
    ReceivingDocumentStatusRequest,
    ReceivingDocumentUpdateRequest,
    ReceivingItemResponse,
)
from app.modules.products.infrastructure.repositories import SQLAlchemyProductRepository
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/receiving-documents", tags=["Receiving Documents"])
logger = logging.getLogger("application")
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
OptionalUUIDQuery = Annotated[UUID | None, Query()]
OptionalSearchQuery = Annotated[str | None, Query(max_length=80)]
OptionalStatusQuery = Annotated[ReceivingDocumentStatus | None, Query()]


def _item_response(item: ReceivingItemModel) -> ReceivingItemResponse:
    return ReceivingItemResponse(
        id=item.id,
        tenant_id=item.tenant_id,
        document_id=item.document_id,
        product_id=item.product_id,
        ordered_quantity=item.ordered_quantity,
        received_quantity=item.received_quantity,
        damaged_quantity=item.damaged_quantity,
        pending_quantity=item.pending_quantity,
        unit_cost=item.unit_cost,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


def _document_response(document: ReceivingDocumentModel) -> ReceivingDocumentResponse:
    return ReceivingDocumentResponse(
        id=document.id,
        tenant_id=document.tenant_id,
        branch_id=document.branch_id,
        warehouse_id=document.warehouse_id,
        supplier_id=document.supplier_id,
        document_number=document.document_number,
        document_type=document.document_type,
        status=document.status,
        expected_date=document.expected_date,
        received_date=document.received_date,
        notes=document.notes,
        items=[_item_response(item) for item in document.items],
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _snapshot(document: ReceivingDocumentModel) -> dict[str, object]:
    return {
        "id": str(document.id),
        "tenant_id": str(document.tenant_id),
        "branch_id": str(document.branch_id),
        "warehouse_id": str(document.warehouse_id),
        "supplier_id": str(document.supplier_id) if document.supplier_id else None,
        "document_number": document.document_number,
        "document_type": document.document_type,
        "status": document.status.value,
        "expected_date": document.expected_date.isoformat() if document.expected_date else None,
        "received_date": document.received_date.isoformat() if document.received_date else None,
        "notes": document.notes,
        "items": [
            {
                "id": str(item.id),
                "product_id": str(item.product_id),
                "ordered_quantity": _decimal_to_string(item.ordered_quantity),
                "received_quantity": _decimal_to_string(item.received_quantity),
                "damaged_quantity": _decimal_to_string(item.damaged_quantity),
                "pending_quantity": _decimal_to_string(item.pending_quantity),
                "unit_cost": _decimal_to_string(item.unit_cost),
            }
            for item in document.items
        ],
    }


def _decimal_to_string(value: Decimal | None) -> str | None:
    return str(value) if value is not None else None


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


def _repositories(
    session: AsyncSession,
) -> tuple[
    SQLAlchemyReceivingDocumentRepository,
    SQLAlchemyWarehouseRepository,
    SQLAlchemyProductRepository,
]:
    return (
        SQLAlchemyReceivingDocumentRepository(session),
        SQLAlchemyWarehouseRepository(session),
        SQLAlchemyProductRepository(session),
    )


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _record_receiving_event(
    session: AsyncSession,
    *,
    event_name: str,
    action: str,
    document: ReceivingDocumentModel,
    current_user: AuthenticatedUser,
    before_data: dict | None = None,
    after_data: dict | None = None,
) -> None:
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name=event_name,
            module="inventory",
            action=action,
            entity_type="receiving_document",
            entity_id=document.id,
            tenant_id=document.tenant_id,
            actor_user_id=current_user.id,
            before_data=before_data,
            after_data=after_data,
        )
    )


@router.get("", response_model=list[ReceivingDocumentResponse])
async def list_receiving_documents(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    warehouse_id: OptionalUUIDQuery = None,
    status: OptionalStatusQuery = None,
    search: OptionalSearchQuery = None,
) -> JSONResponse:
    receiving, _, _ = _repositories(session)
    result = await ListReceivingDocuments(receiving).execute(
        ReceivingDocumentListInput(
            tenant_id=current_user.tenant_id,
            branch_id=current_user.branch_id,
            warehouse_id=warehouse_id,
            status=status,
            search=search,
            page=page,
            page_size=page_size,
        )
    )
    logger.info(
        "receiving_document.query.completed",
        extra={
            "event": "receiving_document.query.completed",
            "tenant_id": str(current_user.tenant_id),
        },
    )
    return success_response(
        "RECEIVING_DOCUMENT_LIST_RETRIEVED",
        data=[_document_response(item).model_dump(mode="json") for item in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/{document_id}", response_model=ReceivingDocumentResponse)
async def get_receiving_document(
    document_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        receiving, _, _ = _repositories(session)
        document = await GetReceivingDocument(receiving).execute(
            document_id,
            tenant_id=current_user.tenant_id,
        )
        return success_response(
            "RECEIVING_DOCUMENT_RETRIEVED",
            data=_document_response(document).model_dump(mode="json"),
        )
    except (ReceivingDocumentError, WarehouseError) as exc:
        return receiving_exception_to_response(exc)


@router.post("", response_model=ReceivingDocumentResponse)
async def create_receiving_document(
    payload: ReceivingDocumentCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        receiving, warehouses, products = _repositories(session)
        document = await CreateReceivingDocument(receiving, warehouses, products).execute(
            ReceivingDocumentCreateInput(
                tenant_id=current_user.tenant_id,
                branch_id=current_user.branch_id,
                warehouse_id=payload.warehouse_id,
                supplier_id=payload.supplier_id,
                document_number=payload.document_number,
                document_type=payload.document_type,
                status=payload.status,
                expected_date=payload.expected_date,
                received_date=payload.received_date,
                notes=payload.notes,
                items=[_item_input(item) for item in payload.items],
                actor_id=current_user.id,
            )
        )
        await _record_receiving_event(
            session,
            event_name="receiving_document.created",
            action="created",
            document=document,
            current_user=current_user,
            after_data=_snapshot(document),
        )
        audit_logger.info(
            "receiving_document.created",
            extra={
                "event": "receiving_document.created",
                "tenant_id": str(current_user.tenant_id),
                "receiving_document_id": str(document.id),
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "RECEIVING_DOCUMENT_CREATED",
            data=_document_response(document).model_dump(mode="json"),
        )
    except (ReceivingDocumentError, WarehouseError, InventoryProductNotFoundError) as exc:
        await session.rollback()
        return receiving_exception_to_response(exc)


@router.put("/{document_id}", response_model=ReceivingDocumentResponse)
async def update_receiving_document(
    document_id: UUID,
    payload: ReceivingDocumentUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        receiving, warehouses, products = _repositories(session)
        current = await GetReceivingDocument(receiving).execute(
            document_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        document = await UpdateReceivingDocument(receiving, warehouses, products).execute(
            document_id,
            tenant_id=current_user.tenant_id,
            input_data=ReceivingDocumentUpdateInput(
                document_number=payload.document_number,
                document_type=payload.document_type,
                supplier_id=payload.supplier_id,
                status=payload.status,
                expected_date=payload.expected_date,
                received_date=payload.received_date,
                notes=payload.notes,
                items=[_item_input(item) for item in payload.items] if payload.items else None,
                actor_id=current_user.id,
            ),
        )
        await _record_receiving_event(
            session,
            event_name="receiving_document.updated",
            action="updated",
            document=document,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(document),
        )
        audit_logger.info(
            "receiving_document.updated",
            extra={"event": "receiving_document.updated", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "RECEIVING_DOCUMENT_UPDATED",
            data=_document_response(document).model_dump(mode="json"),
        )
    except (ReceivingDocumentError, WarehouseError, InventoryProductNotFoundError) as exc:
        await session.rollback()
        return receiving_exception_to_response(exc)


@router.post("/{document_id}/status", response_model=ReceivingDocumentResponse)
async def change_receiving_document_status(
    document_id: UUID,
    payload: ReceivingDocumentStatusRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        receiving, _, _ = _repositories(session)
        current = await GetReceivingDocument(receiving).execute(
            document_id, tenant_id=current_user.tenant_id
        )
        before = _snapshot(current)
        document = await ChangeReceivingDocumentStatus(receiving).execute(
            document_id,
            tenant_id=current_user.tenant_id,
            input_data=ReceivingDocumentStatusInput(
                status=payload.status,
                received_date=payload.received_date,
                actor_id=current_user.id,
            ),
        )
        await _record_receiving_event(
            session,
            event_name="receiving_document.status_changed",
            action="status_changed",
            document=document,
            current_user=current_user,
            before_data=before,
            after_data=_snapshot(document),
        )
        audit_logger.info(
            "receiving_document.status_changed",
            extra={
                "event": "receiving_document.status_changed",
                "request_id": _request_id(request),
            },
        )
        await session.commit()
        return success_response(
            "RECEIVING_DOCUMENT_STATUS_CHANGED",
            data=_document_response(document).model_dump(mode="json"),
        )
    except ReceivingDocumentError as exc:
        await session.rollback()
        return receiving_exception_to_response(exc)


@router.delete("/{document_id}", response_model=ReceivingDocumentResponse)
async def delete_receiving_document(
    document_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        receiving, _, _ = _repositories(session)
        document = await DeleteReceivingDocument(receiving).execute(
            document_id,
            tenant_id=current_user.tenant_id,
            actor_id=current_user.id,
        )
        await _record_receiving_event(
            session,
            event_name="receiving_document.deleted",
            action="deleted",
            document=document,
            current_user=current_user,
            after_data=_snapshot(document),
        )
        audit_logger.info(
            "receiving_document.deleted",
            extra={"event": "receiving_document.deleted", "request_id": _request_id(request)},
        )
        await session.commit()
        return success_response(
            "RECEIVING_DOCUMENT_DELETED",
            data=_document_response(document).model_dump(mode="json"),
        )
    except ReceivingDocumentError as exc:
        await session.rollback()
        return receiving_exception_to_response(exc)


def _item_input(item) -> ReceivingItemInput:
    return ReceivingItemInput(
        product_id=item.product_id,
        ordered_quantity=item.ordered_quantity,
        received_quantity=item.received_quantity,
        damaged_quantity=item.damaged_quantity,
        unit_cost=item.unit_cost,
    )


def receiving_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, ReceivingDocumentNotFoundError):
        return error_response("RECEIVING_DOCUMENT_NOT_FOUND")
    if isinstance(exc, ReceivingDocumentNumberAlreadyExistsError):
        return error_response("RECEIVING_DOCUMENT_NUMBER_ALREADY_EXISTS")
    if isinstance(exc, ReceivingDocumentBranchRequiredError | WarehouseBranchRequiredError):
        return error_response("RECEIVING_DOCUMENT_BRANCH_REQUIRED")
    if isinstance(exc, ReceivingDocumentInvalidDataError):
        return error_response("RECEIVING_DOCUMENT_INVALID_DATA")
    if isinstance(exc, ReceivingDocumentItemRequiredError):
        return error_response("RECEIVING_DOCUMENT_ITEM_REQUIRED")
    if isinstance(exc, InventoryProductNotFoundError):
        return error_response("PRODUCT_NOT_FOUND")
    if isinstance(exc, WarehouseNotFoundError):
        return error_response("WAREHOUSE_NOT_FOUND")
    if isinstance(exc, WarehouseInactiveError):
        return error_response("WAREHOUSE_INACTIVE")
    return error_response("INTERNAL_SERVER_ERROR")
