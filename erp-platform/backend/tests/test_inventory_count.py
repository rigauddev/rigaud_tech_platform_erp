from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.inventory_count_service import (
    InventoryCountCreateInput,
    InventoryCountService,
)
from app.modules.inventory.domain.entities import InventoryCountStatus, InventoryMovementType
from app.modules.inventory.infrastructure.models import InventoryBalanceModel, InventoryCountModel


class _Counts:
    def __init__(self) -> None:
        self.items: dict[UUID, InventoryCountModel] = {}

    async def add(self, count: InventoryCountModel) -> InventoryCountModel:
        self.items[count.id] = count
        return count

    async def get_by_id(self, count_id: UUID, *, tenant_id: UUID):
        count = self.items.get(count_id)
        return count if count and count.tenant_id == tenant_id else None


class _Products:
    def __init__(self, product_id: UUID) -> None:
        self.product_id = product_id

    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID):
        return object() if product_id == self.product_id else None


class _Inventory:
    def __init__(self, tenant_id: UUID, branch_id: UUID, product_id: UUID, warehouse_id: UUID) -> None:
        self.balance = InventoryBalanceModel(id=uuid4(), tenant_id=tenant_id, branch_id=branch_id, product_id=product_id, warehouse_id=warehouse_id, physical_quantity=Decimal("4.000"), reserved_quantity=Decimal("0.000"), putaway_pending_quantity=Decimal("0.000"))
        self.movements = []

    async def get_balance(self, **kwargs):
        return self.balance

    async def get_or_create_balance(self, **kwargs):
        return self.balance

    async def add_balance(self, balance):
        self.balance = balance
        return balance

    async def add_movement(self, movement):
        movement.id = movement.id or uuid4()
        self.movements.append(movement)
        return movement


@pytest.mark.asyncio
async def test_finished_count_creates_immutable_count_movement() -> None:
    tenant_id, branch_id, product_id, warehouse_id = uuid4(), uuid4(), uuid4(), uuid4()
    counts = _Counts()
    inventory = _Inventory(tenant_id, branch_id, product_id, warehouse_id)
    service = InventoryCountService(counts, inventory, _Products(product_id))
    count = await service.create(InventoryCountCreateInput(tenant_id=tenant_id, branch_id=branch_id, warehouse_id=warehouse_id, code="INV-001", product_ids=[product_id]))
    await service.start(count.id, tenant_id=tenant_id, branch_id=branch_id, actor_id=None)
    await service.record_item(count.id, count.items[0].id, Decimal("6.000"), tenant_id=tenant_id, branch_id=branch_id, actor_id=None)
    result = await service.finish(count.id, tenant_id=tenant_id, branch_id=branch_id, actor_id=None)

    assert result.status == InventoryCountStatus.FINISHED
    assert inventory.balance.physical_quantity == Decimal("6.000")
    assert inventory.movements[0].movement_type == InventoryMovementType.COUNT
    assert inventory.movements[0].business_process == "COUNT"


@pytest.mark.asyncio
async def test_cancelled_count_does_not_change_balance() -> None:
    tenant_id, branch_id, product_id, warehouse_id = uuid4(), uuid4(), uuid4(), uuid4()
    counts = _Counts()
    inventory = _Inventory(tenant_id, branch_id, product_id, warehouse_id)
    service = InventoryCountService(counts, inventory, _Products(product_id))
    count = await service.create(InventoryCountCreateInput(tenant_id=tenant_id, branch_id=branch_id, warehouse_id=warehouse_id, code="INV-002", product_ids=[product_id]))
    result = await service.cancel(count.id, tenant_id=tenant_id, branch_id=branch_id, actor_id=None)

    assert result.status == InventoryCountStatus.CANCELLED
    assert inventory.balance.physical_quantity == Decimal("4.000")
    assert not inventory.movements
