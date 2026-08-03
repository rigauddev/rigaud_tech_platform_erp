from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.goods_receipt_service import (
    GoodsReceiptInput,
    GoodsReceiptService,
)
from app.modules.inventory.application.putaway_service import PutAwayInput, PutAwayService
from app.modules.inventory.application.receiving_use_cases import (
    ChangeReceivingDocumentStatus,
    CreateReceivingDocument,
    DeleteReceivingDocument,
    ReceivingDocumentCreateInput,
    ReceivingDocumentStatusInput,
    ReceivingItemInput,
)
from app.modules.inventory.domain.entities import InventoryMovementType, ReceivingDocumentStatus
from app.modules.inventory.domain.exceptions import (
    PutAwayCannotConfirmError,
    ReceivingDocumentCannotConfirmError,
    ReceivingDocumentInvalidDataError,
    ReceivingDocumentNumberAlreadyExistsError,
    WarehouseBranchRequiredError,
)
from app.modules.inventory.domain.receiving_repositories import ReceivingDocumentRepository
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.warehouse_location_repositories import (
    WarehouseLocationRepository,
)
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
    ReceivingDocumentModel,
    WarehouseLocationModel,
    WarehouseModel,
)
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
async def test_goods_receipt_confirms_document_and_keeps_stock_pending_putaway() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    receiving = _FakeReceivingDocumentRepository()
    inventory = _FakeInventoryRepository()
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
            status=ReceivingDocumentStatus.RECEIVING,
            items=[
                ReceivingItemInput(
                    product_id=product.id,
                    ordered_quantity=Decimal("10.000"),
                    received_quantity=Decimal("10.000"),
                )
            ],
        )
    )

    result = await GoodsReceiptService(
        receiving,
        inventory,
        _FakeWarehouseRepository([warehouse]),
    ).confirm(
        GoodsReceiptInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
            actor_id=uuid4(),
        )
    )

    assert result.document.status == ReceivingDocumentStatus.PUTAWAY_PENDING
    assert result.movements[0].movement_type == InventoryMovementType.RECEIPT
    assert result.movements[0].physical_quantity_delta == Decimal("10.000")
    assert result.movements[0].putaway_pending_quantity_delta == Decimal("10.000")
    assert result.balances[0].physical_quantity == Decimal("10.000")
    assert result.balances[0].putaway_pending_quantity == Decimal("10.000")
    assert result.balances[0].available_quantity == Decimal("0.000")


@pytest.mark.asyncio
async def test_putaway_confirms_pending_stock_into_location() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    location = _location(tenant_id, branch_id, warehouse.id)
    receiving = _FakeReceivingDocumentRepository()
    inventory = _FakeInventoryRepository()
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
            items=[
                ReceivingItemInput(
                    product_id=product.id,
                    ordered_quantity=Decimal("10.000"),
                    received_quantity=Decimal("10.000"),
                )
            ],
        )
    )
    await GoodsReceiptService(
        receiving,
        inventory,
        _FakeWarehouseRepository([warehouse]),
    ).confirm(
        GoodsReceiptInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
        )
    )

    result = await PutAwayService(
        receiving,
        inventory,
        _FakeWarehouseLocationRepository([location]),
    ).confirm(
        PutAwayInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
            product_id=product.id,
            location_id=location.id,
            quantity=Decimal("10.000"),
            actor_id=uuid4(),
        )
    )

    assert result.document.status == ReceivingDocumentStatus.AVAILABLE
    assert result.movement.movement_type == InventoryMovementType.PUTAWAY
    assert result.movement.putaway_pending_quantity_delta == Decimal("-10.000")
    assert result.movement.origin_module == "PURCHASE"
    assert result.movement.business_process == "PUTAWAY"
    assert result.source_balance.physical_quantity == Decimal("0.000")
    assert result.source_balance.putaway_pending_quantity == Decimal("0.000")
    assert result.target_balance.physical_quantity == Decimal("10.000")
    assert result.target_balance.available_quantity == Decimal("10.000")


@pytest.mark.asyncio
async def test_putaway_rejects_quantity_above_pending_stock() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    product = _product(tenant_id)
    location = _location(tenant_id, branch_id, warehouse.id)
    receiving = _FakeReceivingDocumentRepository()
    inventory = _FakeInventoryRepository()
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
            items=[
                ReceivingItemInput(
                    product_id=product.id,
                    ordered_quantity=Decimal("2.000"),
                    received_quantity=Decimal("2.000"),
                )
            ],
        )
    )
    await GoodsReceiptService(
        receiving,
        inventory,
        _FakeWarehouseRepository([warehouse]),
    ).confirm(
        GoodsReceiptInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
        )
    )
    await PutAwayService(
        receiving,
        inventory,
        _FakeWarehouseLocationRepository([location]),
    ).confirm(
        PutAwayInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
            product_id=product.id,
            location_id=location.id,
            quantity=Decimal("1.500"),
        )
    )

    with pytest.raises(PutAwayCannotConfirmError):
        await PutAwayService(
            receiving,
            inventory,
            _FakeWarehouseLocationRepository([location]),
        ).confirm(
            PutAwayInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                document_id=document.id,
                product_id=product.id,
                location_id=location.id,
                quantity=Decimal("1.000"),
            )
        )


@pytest.mark.asyncio
async def test_goods_receipt_rejects_already_confirmed_document() -> None:
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
            items=[
                ReceivingItemInput(
                    product_id=product.id,
                    ordered_quantity=Decimal("1.000"),
                    received_quantity=Decimal("1.000"),
                )
            ],
        )
    )
    await GoodsReceiptService(
        receiving,
        _FakeInventoryRepository(),
        _FakeWarehouseRepository([warehouse]),
    ).confirm(
        GoodsReceiptInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            document_id=document.id,
        )
    )

    with pytest.raises(ReceivingDocumentCannotConfirmError):
        await GoodsReceiptService(
            receiving,
            _FakeInventoryRepository(),
            _FakeWarehouseRepository([warehouse]),
        ).confirm(
            GoodsReceiptInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                document_id=document.id,
            )
        )


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


def _location(tenant_id: UUID, branch_id: UUID, warehouse_id: UUID) -> WarehouseLocationModel:
    return WarehouseLocationModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        warehouse_id=warehouse_id,
        zone_id=uuid4(),
        code="A-01-01",
        name="Prateleira A",
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


class _FakeWarehouseLocationRepository(WarehouseLocationRepository):
    def __init__(self, items: list[WarehouseLocationModel] | None = None) -> None:
        self.items = {item.id: item for item in items or []}

    async def add(self, location: WarehouseLocationModel) -> WarehouseLocationModel:
        self.items[location.id] = location
        return location

    async def get_by_id(
        self, location_id: UUID, *, tenant_id: UUID
    ) -> WarehouseLocationModel | None:
        location = self.items.get(location_id)
        if location and location.tenant_id == tenant_id and location.deleted_at is None:
            return location
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseLocationModel]:
        return list(self.items.values())[offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
    ) -> int:
        return len(self.items)

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        warehouse_id: UUID,
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

    async def exists_by_qr_code(
        self,
        qr_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return False


class _FakeInventoryRepository(InventoryRepository):
    def __init__(self) -> None:
        self.balances: dict[
            tuple[UUID, UUID, UUID, UUID | None, UUID | None], InventoryBalanceModel
        ] = {}
        self.movements: list[InventoryMovementModel] = []

    async def add_balance(self, balance: InventoryBalanceModel) -> InventoryBalanceModel:
        key = (
            balance.tenant_id,
            balance.branch_id,
            balance.product_id,
            balance.warehouse_id,
            balance.location_id,
        )
        self.balances[key] = balance
        return balance

    async def add_movement(self, movement: InventoryMovementModel) -> InventoryMovementModel:
        if movement.id is None:
            movement.id = uuid4()
        self.movements.append(movement)
        return movement

    async def add_adjustment(
        self, adjustment: InventoryAdjustmentModel
    ) -> InventoryAdjustmentModel:
        return adjustment

    async def add_reservation(
        self, reservation: InventoryReservationModel
    ) -> InventoryReservationModel:
        return reservation

    async def get_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel | None:
        return self.balances.get((tenant_id, branch_id, product_id, warehouse_id, location_id))

    async def get_or_create_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel:
        balance = await self.get_balance(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
        )
        if balance is not None:
            return balance
        balance = InventoryBalanceModel(
            id=uuid4(),
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            physical_quantity=Decimal("0.000"),
            reserved_quantity=Decimal("0.000"),
            putaway_pending_quantity=Decimal("0.000"),
        )
        return await self.add_balance(balance)

    async def list_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryBalanceModel]:
        return list(self.balances.values())[offset : offset + limit]

    async def count_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        return len(self.balances)

    async def list_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryMovementModel]:
        return self.movements[offset : offset + limit]

    async def count_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        return len(self.movements)

    async def get_reservation_by_id(
        self, reservation_id: UUID, *, tenant_id: UUID
    ) -> InventoryReservationModel | None:
        return None
