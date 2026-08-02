from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.use_cases import (
    CreateInventoryAdjustment,
    CreateInventoryReservation,
    InventoryAdjustmentInput,
    InventoryReservationInput,
)
from app.modules.inventory.domain.entities import (
    InventoryAdjustmentType,
    InventoryMovementType,
)
from app.modules.inventory.domain.exceptions import InventoryInsufficientStockError
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
        limit: int,
        offset: int,
    ) -> list[InventoryMovementModel]:
        return self.movements

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
        return next(
            (
                reservation
                for reservation in self.reservations
                if reservation.id == reservation_id and reservation.tenant_id == tenant_id
            ),
            None,
        )


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
