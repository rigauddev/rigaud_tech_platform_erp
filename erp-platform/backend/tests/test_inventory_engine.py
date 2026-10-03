from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.use_cases import (
    CreateInventoryAdjustment,
    CreateInventoryReservation,
    GetInventoryTransaction,
    InventoryAdjustmentInput,
    InventoryListInput,
    InventoryReservationInput,
    ListInventoryTransactions,
    ReverseInventoryAdjustment,
)
from app.modules.inventory.domain.entities import (
    InventoryAdjustmentType,
    InventoryMovementType,
)
from app.modules.inventory.domain.exceptions import (
    InventoryInsufficientStockError,
    InventoryMovementNotFoundError,
)
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
)
from app.modules.products.domain.repositories import ProductRepository


@pytest.mark.asyncio
async def test_adjustment_in_creates_balance_and_movement() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    product_id = uuid4()
    inventory = _FakeInventoryRepository()

    result = await CreateInventoryAdjustment(inventory, _FakeProductRepository()).execute(
        InventoryAdjustmentInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            adjustment_type=InventoryAdjustmentType.INCREASE,
            quantity="10",
            reason="Entrada inicial",
            actor_id=uuid4(),
        )
    )

    assert result.balance.physical_quantity == Decimal("10.000")
    assert result.balance.reserved_quantity == Decimal("0.000")
    assert result.balance.available_quantity == Decimal("10.000")
    assert result.movement.movement_type == InventoryMovementType.ADJUSTMENT_IN
    assert result.movement.physical_quantity_delta == Decimal("10.000")


@pytest.mark.asyncio
async def test_reservation_changes_only_reserved_quantity() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    product_id = uuid4()
    inventory = _FakeInventoryRepository()
    inventory.balance = InventoryBalanceModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        product_id=product_id,
        physical_quantity=Decimal("8.000"),
        reserved_quantity=Decimal("1.000"),
    )

    result = await CreateInventoryReservation(inventory, _FakeProductRepository()).execute(
        InventoryReservationInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            quantity="2",
            reason="Pedido em aberto",
            source_module="restaurant",
            actor_id=uuid4(),
        )
    )

    assert result.balance.physical_quantity == Decimal("8.000")
    assert result.balance.reserved_quantity == Decimal("3.000")
    assert result.balance.available_quantity == Decimal("5.000")
    assert result.movement.movement_type == InventoryMovementType.RESERVATION_CREATED
    assert result.movement.reserved_quantity_delta == Decimal("2.000")


@pytest.mark.asyncio
async def test_adjustment_reversal_creates_compensating_movement() -> None:
    tenant_id, branch_id, product_id = uuid4(), uuid4(), uuid4()
    inventory = _FakeInventoryRepository()
    created = await CreateInventoryAdjustment(inventory, _FakeProductRepository()).execute(
        InventoryAdjustmentInput(tenant_id=tenant_id, branch_id=branch_id, product_id=product_id, adjustment_type=InventoryAdjustmentType.INCREASE, quantity="5", reason="Correção")
    )
    result = await ReverseInventoryAdjustment(inventory, _FakeProductRepository()).execute(
        created.adjustment.id, tenant_id=tenant_id, branch_id=branch_id, reason="Estorno autorizado", actor_id=None
    )
    assert result.balance.physical_quantity == Decimal("0.000")
    assert result.adjustment.reversal_of_id == created.adjustment.id
    assert len(inventory.movements) == 2


@pytest.mark.asyncio
async def test_reservation_fails_when_available_stock_is_insufficient() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    product_id = uuid4()
    inventory = _FakeInventoryRepository()
    inventory.balance = InventoryBalanceModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        product_id=product_id,
        physical_quantity=Decimal("2.000"),
        reserved_quantity=Decimal("1.500"),
    )

    with pytest.raises(InventoryInsufficientStockError):
        await CreateInventoryReservation(inventory, _FakeProductRepository()).execute(
            InventoryReservationInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                product_id=product_id,
                quantity="1",
                reason="Pedido em aberto",
            )
        )


@pytest.mark.asyncio
async def test_transactions_filter_and_detail_are_tenant_and_branch_scoped() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    movement_id = uuid4()
    inventory = _FakeInventoryRepository()
    inventory.movements.append(
        InventoryMovementModel(
            id=movement_id,
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=uuid4(),
            movement_type=InventoryMovementType.ADJUSTMENT_IN,
            physical_quantity_delta=Decimal("4.000"),
            reserved_quantity_delta=Decimal("0.000"),
            putaway_pending_quantity_delta=Decimal("0.000"),
            reason="Entrada inicial",
            origin_module="ADJUSTMENT",
            business_process="ADJUSTMENT",
            source_module="inventory",
            event_name="inventory.adjusted.in",
        )
    )
    inventory.movements.append(
        InventoryMovementModel(
            id=uuid4(),
            tenant_id=tenant_id,
            branch_id=uuid4(),
            product_id=uuid4(),
            movement_type=InventoryMovementType.PUTAWAY,
            physical_quantity_delta=Decimal("0.000"),
            reserved_quantity_delta=Decimal("0.000"),
            putaway_pending_quantity_delta=Decimal("-1.000"),
            reason="Put Away",
            origin_module="PURCHASE",
            business_process="PUTAWAY",
            source_module="receiving",
            event_name="inventory.putaway.confirmed",
        )
    )

    result = await ListInventoryTransactions(inventory).execute(
        InventoryListInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            origin_module="adjustment",
            business_process="adjustment",
        )
    )

    assert result.total == 1
    assert result.items[0].id == movement_id
    transaction = await GetInventoryTransaction(inventory).execute(
        movement_id,
        tenant_id=tenant_id,
        branch_id=branch_id,
    )
    assert transaction.event_name == "inventory.adjusted.in"

    with pytest.raises(InventoryMovementNotFoundError):
        await GetInventoryTransaction(inventory).execute(
            movement_id,
            tenant_id=tenant_id,
            branch_id=uuid4(),
        )


class _FakeInventoryRepository(InventoryRepository):
    def __init__(self) -> None:
        self.balance: InventoryBalanceModel | None = None
        self.movements: list[InventoryMovementModel] = []
        self.adjustments: list[InventoryAdjustmentModel] = []
        self.reservations: list[InventoryReservationModel] = []

    async def add_balance(self, balance: InventoryBalanceModel) -> InventoryBalanceModel:
        self.balance = balance
        return balance

    async def add_movement(self, movement: InventoryMovementModel) -> InventoryMovementModel:
        movement.id = movement.id or uuid4()
        self.movements.append(movement)
        return movement

    async def add_adjustment(
        self, adjustment: InventoryAdjustmentModel
    ) -> InventoryAdjustmentModel:
        adjustment.id = adjustment.id or uuid4()
        self.adjustments.append(adjustment)
        return adjustment

    async def add_reservation(
        self, reservation: InventoryReservationModel
    ) -> InventoryReservationModel:
        reservation.id = reservation.id or uuid4()
        self.reservations.append(reservation)
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
        if (
            self.balance
            and self.balance.tenant_id == tenant_id
            and self.balance.branch_id == branch_id
            and self.balance.product_id == product_id
            and self.balance.warehouse_id == warehouse_id
            and self.balance.location_id == location_id
        ):
            return self.balance
        return None

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
        if balance:
            return balance
        self.balance = InventoryBalanceModel(
            id=uuid4(),
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            physical_quantity=Decimal("0.000"),
            reserved_quantity=Decimal("0.000"),
        )
        return self.balance

    async def list_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryBalanceModel]:
        return [self.balance] if self.balance else []

    async def count_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        return len(
            await self.list_balances(
                tenant_id=tenant_id,
                branch_id=branch_id,
                product_id=product_id,
                limit=100,
                offset=0,
            )
        )

    async def list_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        warehouse_id: UUID | None,
        location_id: UUID | None,
        movement_type: InventoryMovementType | None,
        origin_module: str | None,
        business_process: str | None,
        source_module: str | None,
        limit: int,
        offset: int,
    ) -> list[InventoryMovementModel]:
        items = [
            movement
            for movement in self.movements
            if movement.tenant_id == tenant_id
            and (branch_id is None or movement.branch_id == branch_id)
            and (product_id is None or movement.product_id == product_id)
            and (warehouse_id is None or movement.warehouse_id == warehouse_id)
            and (location_id is None or movement.location_id == location_id)
            and (movement_type is None or movement.movement_type == movement_type)
            and (origin_module is None or movement.origin_module == origin_module)
            and (business_process is None or movement.business_process == business_process)
            and (source_module is None or movement.source_module == source_module)
        ]
        return items[offset : offset + limit]

    async def count_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        warehouse_id: UUID | None,
        location_id: UUID | None,
        movement_type: InventoryMovementType | None,
        origin_module: str | None,
        business_process: str | None,
        source_module: str | None,
    ) -> int:
        return len(
            await self.list_movements(
                tenant_id=tenant_id,
                branch_id=branch_id,
                product_id=product_id,
                warehouse_id=warehouse_id,
                location_id=location_id,
                movement_type=movement_type,
                origin_module=origin_module,
                business_process=business_process,
                source_module=source_module,
                limit=100,
                offset=0,
            )
        )

    async def get_movement_by_id(
        self,
        movement_id: UUID,
        *,
        tenant_id: UUID,
    ) -> InventoryMovementModel | None:
        return next(
            (
                movement
                for movement in self.movements
                if movement.id == movement_id and movement.tenant_id == tenant_id
            ),
            None,
        )

    async def get_reservation_by_id(
        self, reservation_id: UUID, *, tenant_id: UUID
    ) -> InventoryReservationModel | None:
        return next(
            (
                reservation
                for reservation in self.reservations
                if reservation.id == reservation_id and reservation.tenant_id == tenant_id
            ),
            None,
        )

    async def get_adjustment_by_id(
        self, adjustment_id: UUID, *, tenant_id: UUID
    ) -> InventoryAdjustmentModel | None:
        return next((item for item in self.adjustments if item.id == adjustment_id and item.tenant_id == tenant_id), None)

    async def has_adjustment_reversal(self, adjustment_id: UUID, *, tenant_id: UUID) -> bool:
        return any(item.tenant_id == tenant_id and item.reversal_of_id == adjustment_id for item in self.adjustments)


class _FakeProductRepository(ProductRepository):
    async def add(self, product):
        return product

    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID):
        return object()

    async def list(self, **kwargs):
        return []

    async def count(self, **kwargs) -> int:
        return 0

    async def exists_by_internal_code(
        self, internal_code: str, *, tenant_id: UUID, exclude_id=None
    ):
        return False

    async def exists_by_barcode(self, barcode: str, *, tenant_id: UUID, exclude_id=None):
        return False
