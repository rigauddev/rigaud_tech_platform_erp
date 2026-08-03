from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.modules.inventory.application.validators import (
    normalize_optional_receiving_text,
    normalize_receiving_document_number,
    normalize_receiving_money,
    normalize_receiving_quantity,
    normalize_receiving_text,
)
from app.modules.inventory.domain.entities import ReceivingDocumentStatus
from app.modules.inventory.domain.exceptions import (
    InventoryProductNotFoundError,
    ReceivingDocumentBranchRequiredError,
    ReceivingDocumentInvalidDataError,
    ReceivingDocumentItemRequiredError,
    ReceivingDocumentNotFoundError,
    ReceivingDocumentNumberAlreadyExistsError,
    WarehouseBranchRequiredError,
    WarehouseInactiveError,
    WarehouseNotFoundError,
)
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import (
    ReceivingDocumentModel,
    ReceivingItemModel,
    WarehouseModel,
)
from app.modules.products.domain.repositories import ProductRepository


@dataclass(frozen=True)
class ReceivingItemInput:
    product_id: UUID
    ordered_quantity: Decimal | str | int
    received_quantity: Decimal | str | int = Decimal("0.000")
    damaged_quantity: Decimal | str | int = Decimal("0.000")
    unit_cost: Decimal | str | int | None = None


@dataclass(frozen=True)
class ReceivingDocumentCreateInput:
    tenant_id: UUID
    branch_id: UUID | None
    warehouse_id: UUID
    document_number: str
    document_type: str
    supplier_id: UUID | None = None
    status: ReceivingDocumentStatus = ReceivingDocumentStatus.DRAFT
    expected_date: datetime | None = None
    received_date: datetime | None = None
    notes: str | None = None
    items: list[ReceivingItemInput] | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ReceivingDocumentUpdateInput:
    document_number: str | None = None
    document_type: str | None = None
    supplier_id: UUID | None = None
    status: ReceivingDocumentStatus | None = None
    expected_date: datetime | None = None
    received_date: datetime | None = None
    notes: str | None = None
    items: list[ReceivingItemInput] | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ReceivingDocumentStatusInput:
    status: ReceivingDocumentStatus
    received_date: datetime | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class ReceivingDocumentListInput:
    tenant_id: UUID
    branch_id: UUID | None = None
    warehouse_id: UUID | None = None
    status: ReceivingDocumentStatus | None = None
    search: str | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class ReceivingDocumentListResult:
    items: list[ReceivingDocumentModel]
    total: int
    page: int
    page_size: int


class CreateReceivingDocument:
    def __init__(
        self,
        receiving: ReceivingDocumentRepository,
        warehouses: WarehouseRepository,
        products: ProductRepository,
    ) -> None:
        self.receiving = receiving
        self.warehouses = warehouses
        self.products = products

    async def execute(self, input_data: ReceivingDocumentCreateInput) -> ReceivingDocumentModel:
        branch_id = _require_branch(input_data.branch_id)
        warehouse = await _get_active_warehouse(
            self.warehouses,
            input_data.warehouse_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        )
        document_number = normalize_receiving_document_number(input_data.document_number)
        if await self.receiving.exists_by_document_number(
            document_number,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        ):
            raise ReceivingDocumentNumberAlreadyExistsError("Receiving document exists.")
        items = await _build_items(
            input_data.items,
            tenant_id=input_data.tenant_id,
            products=self.products,
        )
        document = ReceivingDocumentModel(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            supplier_id=input_data.supplier_id,
            document_number=document_number,
            document_type=normalize_receiving_text(
                input_data.document_type,
                "document_type",
                max_length=40,
            ),
            status=input_data.status,
            expected_date=input_data.expected_date,
            received_date=input_data.received_date,
            notes=normalize_optional_receiving_text(input_data.notes, "notes", max_length=1000),
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
            items=items,
        )
        return await self.receiving.add(document)


class ListReceivingDocuments:
    def __init__(self, receiving: ReceivingDocumentRepository) -> None:
        self.receiving = receiving

    async def execute(self, input_data: ReceivingDocumentListInput) -> ReceivingDocumentListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        items = await self.receiving.list(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            status=input_data.status,
            search=search,
            limit=page_size,
            offset=offset,
        )
        total = await self.receiving.count(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            status=input_data.status,
            search=search,
        )
        return ReceivingDocumentListResult(items=items, total=total, page=page, page_size=page_size)


class GetReceivingDocument:
    def __init__(self, receiving: ReceivingDocumentRepository) -> None:
        self.receiving = receiving

    async def execute(self, document_id: UUID, *, tenant_id: UUID) -> ReceivingDocumentModel:
        document = await self.receiving.get_by_id(document_id, tenant_id=tenant_id)
        if document is None:
            raise ReceivingDocumentNotFoundError("Receiving document not found.")
        return document


class UpdateReceivingDocument:
    def __init__(
        self,
        receiving: ReceivingDocumentRepository,
        warehouses: WarehouseRepository,
        products: ProductRepository,
    ) -> None:
        self.receiving = receiving
        self.warehouses = warehouses
        self.products = products

    async def execute(
        self,
        document_id: UUID,
        *,
        tenant_id: UUID,
        input_data: ReceivingDocumentUpdateInput,
    ) -> ReceivingDocumentModel:
        document = await GetReceivingDocument(self.receiving).execute(
            document_id,
            tenant_id=tenant_id,
        )
        await _get_active_warehouse(
            self.warehouses,
            document.warehouse_id,
            tenant_id=tenant_id,
            branch_id=document.branch_id,
        )
        if input_data.document_number is not None:
            document_number = normalize_receiving_document_number(input_data.document_number)
            if await self.receiving.exists_by_document_number(
                document_number,
                tenant_id=tenant_id,
                branch_id=document.branch_id,
                exclude_id=document.id,
            ):
                raise ReceivingDocumentNumberAlreadyExistsError("Receiving document exists.")
            document.document_number = document_number
        if input_data.document_type is not None:
            document.document_type = normalize_receiving_text(
                input_data.document_type,
                "document_type",
                max_length=40,
            )
        if input_data.supplier_id is not None:
            document.supplier_id = input_data.supplier_id
        if input_data.status is not None:
            document.status = input_data.status
        if input_data.expected_date is not None:
            document.expected_date = input_data.expected_date
        if input_data.received_date is not None:
            document.received_date = input_data.received_date
        if input_data.notes is not None:
            document.notes = normalize_optional_receiving_text(
                input_data.notes, "notes", max_length=1000
            )
        if input_data.items is not None:
            document.items = await _build_items(
                input_data.items,
                tenant_id=tenant_id,
                products=self.products,
            )
        document.updated_by = input_data.actor_id
        return await self.receiving.add(document)


class ChangeReceivingDocumentStatus:
    def __init__(self, receiving: ReceivingDocumentRepository) -> None:
        self.receiving = receiving

    async def execute(
        self,
        document_id: UUID,
        *,
        tenant_id: UUID,
        input_data: ReceivingDocumentStatusInput,
    ) -> ReceivingDocumentModel:
        document = await GetReceivingDocument(self.receiving).execute(
            document_id,
            tenant_id=tenant_id,
        )
        document.status = input_data.status
        if input_data.received_date is not None:
            document.received_date = input_data.received_date
        document.updated_by = input_data.actor_id
        return await self.receiving.add(document)


class DeleteReceivingDocument:
    def __init__(self, receiving: ReceivingDocumentRepository) -> None:
        self.receiving = receiving

    async def execute(
        self,
        document_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None,
    ) -> ReceivingDocumentModel:
        document = await GetReceivingDocument(self.receiving).execute(
            document_id,
            tenant_id=tenant_id,
        )
        document.status = ReceivingDocumentStatus.CANCELLED
        document.mark_as_deleted()
        document.deleted_by = actor_id
        return await self.receiving.add(document)


def _require_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise ReceivingDocumentBranchRequiredError("Active branch is required.")
    return branch_id


async def _get_active_warehouse(
    warehouses: WarehouseRepository,
    warehouse_id: UUID,
    *,
    tenant_id: UUID,
    branch_id: UUID,
) -> WarehouseModel:
    warehouse = await warehouses.get_by_id(warehouse_id, tenant_id=tenant_id)
    if warehouse is None:
        raise WarehouseNotFoundError("Warehouse not found.")
    if warehouse.branch_id != branch_id:
        raise WarehouseBranchRequiredError("Warehouse belongs to another branch.")
    if not warehouse.is_active:
        raise WarehouseInactiveError("Warehouse is inactive.")
    return warehouse


async def _build_items(
    items: list[ReceivingItemInput] | None,
    *,
    tenant_id: UUID,
    products: ProductRepository,
) -> list[ReceivingItemModel]:
    if not items:
        raise ReceivingDocumentItemRequiredError("Receiving document requires items.")
    models: list[ReceivingItemModel] = []
    for item in items:
        product = await products.get_by_id(item.product_id, tenant_id=tenant_id)
        if product is None:
            raise InventoryProductNotFoundError("Product not found.")
        ordered = normalize_receiving_quantity(item.ordered_quantity, "ordered_quantity")
        received = normalize_receiving_quantity(item.received_quantity, "received_quantity")
        damaged = normalize_receiving_quantity(item.damaged_quantity, "damaged_quantity")
        pending = ordered - received - damaged
        if pending < 0:
            raise ReceivingDocumentInvalidDataError(
                "received_quantity plus damaged_quantity cannot exceed ordered_quantity."
            )
        models.append(
            ReceivingItemModel(
                tenant_id=tenant_id,
                product_id=item.product_id,
                ordered_quantity=ordered,
                received_quantity=received,
                damaged_quantity=damaged,
                pending_quantity=pending,
                unit_cost=normalize_receiving_money(item.unit_cost, "unit_cost"),
            )
        )
    return models
