from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.receiving_use_cases import (
    ChangeReceivingDocumentStatus,
    CreateReceivingDocument,
    DeleteReceivingDocument,
    ReceivingDocumentCreateInput,
    ReceivingDocumentStatusInput,
    ReceivingItemInput,
)
from app.modules.inventory.domain.entities import ReceivingDocumentStatus
from app.modules.inventory.domain.exceptions import (
    ReceivingDocumentInvalidDataError,
    ReceivingDocumentNumberAlreadyExistsError,
    WarehouseBranchRequiredError,
)
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import ReceivingDocumentModel, WarehouseModel
from app.modules.products.domain.entities import ProductType, UnitOfMeasure
from app.modules.products.domain.repositories import ProductRepository
from app.modules.products.infrastructure.models import ProductModel


@pytest.mark.asyncio
async def test_create_receiving_document_calculates_pending_without_stock_movement() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    receiving = _FakeReceivingDocumentRepository()

    document = await CreateReceivingDocument(
        receiving,
        _FakeWarehouseRepository([warehouse]),
        _FakeProductRepository([product]),
    ).execute(
        ReceivingDocumentCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            document_number=" nf-001 ",
            document_type="invoice",
            status=ReceivingDocumentStatus.EXPECTED,
            items=[
                ReceivingItemInput(
                    product_id=product.id,
                    ordered_quantity=Decimal("10.000"),
                    received_quantity=Decimal("3.000"),
                    damaged_quantity=Decimal("1.000"),
                    unit_cost=Decimal("12.50"),
                )
            ],
        )
    )

    assert document.document_number == "NF-001"
    assert document.status == ReceivingDocumentStatus.EXPECTED
    assert document.items[0].pending_quantity == Decimal("6.000")
    assert receiving.stock_movements_created == 0
    assert receiving.balances_changed == 0


@pytest.mark.asyncio
async def test_create_receiving_document_rejects_duplicate_number_in_branch() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    receiving = _FakeReceivingDocumentRepository()
    use_case = CreateReceivingDocument(
        receiving,
        _FakeWarehouseRepository([warehouse]),
        _FakeProductRepository([product]),
    )
    input_data = ReceivingDocumentCreateInput(
        tenant_id=tenant_id,
        branch_id=branch_id,
        warehouse_id=warehouse.id,
        document_number="NF-001",
        document_type="invoice",
        items=[ReceivingItemInput(product_id=product.id, ordered_quantity=Decimal("1.000"))],
    )
    await use_case.execute(input_data)

    with pytest.raises(ReceivingDocumentNumberAlreadyExistsError):
        await use_case.execute(input_data)


@pytest.mark.asyncio
async def test_create_receiving_document_rejects_quantities_above_ordered() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)

    with pytest.raises(ReceivingDocumentInvalidDataError):
        await CreateReceivingDocument(
            _FakeReceivingDocumentRepository(),
            _FakeWarehouseRepository([warehouse]),
            _FakeProductRepository([product]),
        ).execute(
            ReceivingDocumentCreateInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse.id,
                document_number="NF-001",
                document_type="invoice",
                items=[
                    ReceivingItemInput(
                        product_id=product.id,
                        ordered_quantity=Decimal("5.000"),
                        received_quantity=Decimal("4.000"),
                        damaged_quantity=Decimal("2.000"),
                    )
                ],
            )
        )


@pytest.mark.asyncio
async def test_create_receiving_document_rejects_warehouse_from_another_branch() -> None:
    tenant_id = uuid4()
    warehouse = _warehouse(tenant_id, uuid4())
    product = _product(tenant_id)

    with pytest.raises(WarehouseBranchRequiredError):
        await CreateReceivingDocument(
            _FakeReceivingDocumentRepository(),
            _FakeWarehouseRepository([warehouse]),
            _FakeProductRepository([product]),
        ).execute(
            ReceivingDocumentCreateInput(
                tenant_id=tenant_id,
                branch_id=uuid4(),
                warehouse_id=warehouse.id,
                document_number="NF-001",
                document_type="invoice",
                items=[ReceivingItemInput(product_id=product.id, ordered_quantity=Decimal(1))],
            )
        )


@pytest.mark.asyncio
async def test_status_change_and_delete_do_not_move_stock() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    receiving = _FakeReceivingDocumentRepository()
    document = await CreateReceivingDocument(
        receiving,
        _FakeWarehouseRepository([warehouse]),
        _FakeProductRepository([product]),
    ).execute(
        ReceivingDocumentCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            document_number="NF-001",
            document_type="invoice",
            items=[ReceivingItemInput(product_id=product.id, ordered_quantity=Decimal(1))],
        )
    )

    changed = await ChangeReceivingDocumentStatus(receiving).execute(
        document.id,
        tenant_id=tenant_id,
        input_data=ReceivingDocumentStatusInput(status=ReceivingDocumentStatus.RECEIVING),
    )
    assert changed.status == ReceivingDocumentStatus.RECEIVING

    deleted = await DeleteReceivingDocument(receiving).execute(
        document.id,
        tenant_id=tenant_id,
        actor_id=uuid4(),
    )

    assert deleted.status == ReceivingDocumentStatus.CANCELLED
    assert deleted.deleted_at is not None
    assert receiving.stock_movements_created == 0
    assert receiving.balances_changed == 0


def _warehouse(tenant_id: UUID, branch_id: UUID) -> WarehouseModel:
    return WarehouseModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        code="MAIN",
        name="Deposito Principal",
        is_active=True,
    )


def _product(tenant_id: UUID) -> ProductModel:
    return ProductModel(
        id=uuid4(),
        tenant_id=tenant_id,
        name="Produto Demo",
        internal_code="PRD-001",
        product_type=ProductType.SIMPLE,
        unit_of_measure=UnitOfMeasure.UNIT,
        is_active=True,
    )


class _FakeReceivingDocumentRepository(ReceivingDocumentRepository):
    def __init__(self, items: list[ReceivingDocumentModel] | None = None) -> None:
        self.items = {item.id: item for item in items or []}
        self.stock_movements_created = 0
        self.balances_changed = 0

    async def add(self, document: ReceivingDocumentModel) -> ReceivingDocumentModel:
        if document.id is None:
            document.id = uuid4()
        self.items[document.id] = document
        return document

    async def get_by_id(
        self, document_id: UUID, *, tenant_id: UUID
    ) -> ReceivingDocumentModel | None:
        document = self.items.get(document_id)
        if document and document.tenant_id == tenant_id and document.deleted_at is None:
            return document
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
        limit: int,
        offset: int,
    ) -> list[ReceivingDocumentModel]:
        return [
            item
            for item in self.items.values()
            if item.tenant_id == tenant_id
            and (branch_id is None or item.branch_id == branch_id)
            and (warehouse_id is None or item.warehouse_id == warehouse_id)
            and (status is None or item.status == status)
            and (search is None or search.lower() in item.document_number.lower())
        ][offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        status: ReceivingDocumentStatus | None,
        search: str | None,
    ) -> int:
        return len(
            await self.list(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse_id,
                status=status,
                search=search,
                limit=100,
                offset=0,
            )
        )

    async def exists_by_document_number(
        self,
        document_number: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return any(
            item.tenant_id == tenant_id
            and item.branch_id == branch_id
            and item.document_number == document_number
            and item.deleted_at is None
            and item.id != exclude_id
            for item in self.items.values()
        )


class _FakeWarehouseRepository(WarehouseRepository):
    def __init__(self, items: list[WarehouseModel] | None = None) -> None:
        self.items = {item.id: item for item in items or []}

    async def add(self, warehouse: WarehouseModel) -> WarehouseModel:
        self.items[warehouse.id] = warehouse
        return warehouse

    async def get_by_id(self, warehouse_id: UUID, *, tenant_id: UUID) -> WarehouseModel | None:
        warehouse = self.items.get(warehouse_id)
        if warehouse and warehouse.tenant_id == tenant_id and warehouse.deleted_at is None:
            return warehouse
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseModel]:
        return list(self.items.values())[offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        return len(self.items)

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return False

    async def unset_default_for_branch(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        except_id: UUID | None = None,
    ) -> None:
        return None


class _FakeProductRepository(ProductRepository):
    def __init__(self, items: list[ProductModel] | None = None) -> None:
        self.items = {item.id: item for item in items or []}

    async def add(self, product: ProductModel) -> ProductModel:
        self.items[product.id] = product
        return product

    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID) -> ProductModel | None:
        product = self.items.get(product_id)
        if product and product.tenant_id == tenant_id and product.deleted_at is None:
            return product
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        limit: int,
        offset: int,
        product_type: ProductType | None = None,
        unit_of_measure: UnitOfMeasure | None = None,
        is_active: bool | None = None,
        is_available_for_sale: bool | None = None,
        search: str | None = None,
    ) -> list[ProductModel]:
        return list(self.items.values())[offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        product_type: ProductType | None = None,
        unit_of_measure: UnitOfMeasure | None = None,
        is_active: bool | None = None,
        is_available_for_sale: bool | None = None,
        search: str | None = None,
    ) -> int:
        return len(self.items)

    async def exists_by_internal_code(
        self,
        internal_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return False

    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return False
