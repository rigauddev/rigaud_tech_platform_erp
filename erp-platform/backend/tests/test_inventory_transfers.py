from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.inventory_transfer_service import (
    InventoryTransferCreateInput,
    InventoryTransferService,
)
from app.modules.inventory.domain.entities import (
    InventoryMovementType,
    InventoryTransferStatus,
)
from app.modules.inventory.domain.exceptions import InventoryInsufficientStockError
from app.modules.inventory.infrastructure.models import InventoryBalanceModel


class _Transfers:
    def __init__(self) -> None:
        self.items = {}

    async def add(self, transfer):
        self.items[transfer.id] = transfer
        return transfer

    async def get_by_id(self, transfer_id: UUID, *, tenant_id: UUID):
        item = self.items.get(transfer_id)
        return item if item and item.tenant_id == tenant_id else None


class _Inventory:
    def __init__(self, tenant_id: UUID, source_branch_id: UUID, source_warehouse_id: UUID, product_id: UUID) -> None:
        self.balances = {(source_branch_id, source_warehouse_id, None): InventoryBalanceModel(
            id=uuid4(), tenant_id=tenant_id, branch_id=source_branch_id,
            product_id=product_id, warehouse_id=source_warehouse_id,
            physical_quantity=Decimal("10.000"), reserved_quantity=Decimal("0.000"),
            putaway_pending_quantity=Decimal("0.000"),
        )}
        self.movements = []

    async def get_balance(self, *, branch_id, warehouse_id, location_id=None, **_):
        return self.balances.get((branch_id, warehouse_id, location_id))

    async def get_or_create_balance(self, *, tenant_id, branch_id, product_id, warehouse_id, location_id=None):
        key = (branch_id, warehouse_id, location_id)
        if key not in self.balances:
            self.balances[key] = InventoryBalanceModel(
                id=uuid4(), tenant_id=tenant_id, branch_id=branch_id, product_id=product_id,
                warehouse_id=warehouse_id, location_id=location_id,
                physical_quantity=Decimal("0.000"), reserved_quantity=Decimal("0.000"),
                putaway_pending_quantity=Decimal("0.000"),
            )
        return self.balances[key]

    async def add_balance(self, balance):
        return balance

    async def add_movement(self, movement):
        movement.id = movement.id or uuid4()
        self.movements.append(movement)
        return movement


class _Products:
    async def get_by_id(self, product_id: UUID, *, tenant_id: UUID):
        return object()


class _Warehouses:
    def __init__(self, warehouses):
        self.warehouses = warehouses

    async def get_by_id(self, warehouse_id: UUID, *, tenant_id: UUID):
        return self.warehouses.get(warehouse_id)


class _Locations:
    async def get_by_id(self, location_id: UUID, *, tenant_id: UUID):
        return None


class _Warehouse:
    def __init__(self, branch_id: UUID) -> None:
        self.branch_id = branch_id
        self.is_active = True


def _service(tenant_id, source_branch_id, source_warehouse_id, product_id, target_branch_id, target_warehouse_id):
    return InventoryTransferService(
        _Transfers(), _Inventory(tenant_id, source_branch_id, source_warehouse_id, product_id),
        _Products(), _Warehouses({source_warehouse_id: _Warehouse(source_branch_id), target_warehouse_id: _Warehouse(target_branch_id)}), _Locations(),
    )


@pytest.mark.asyncio
async def test_transfer_dispatch_and_receipt_create_separate_immutable_movements() -> None:
    tenant_id, product_id = uuid4(), uuid4()
    source_branch_id, target_branch_id = uuid4(), uuid4()
    source_warehouse_id, target_warehouse_id = uuid4(), uuid4()
    service = _service(tenant_id, source_branch_id, source_warehouse_id, product_id, target_branch_id, target_warehouse_id)
    transfer = await service.create(InventoryTransferCreateInput(
        tenant_id=tenant_id, source_branch_id=source_branch_id, source_warehouse_id=source_warehouse_id,
        target_branch_id=target_branch_id, target_warehouse_id=target_warehouse_id, product_id=product_id,
        quantity=Decimal(3), code="TRF-001", reason="Reposição da filial",
    ))

    assert transfer.status == InventoryTransferStatus.REQUESTED
    assert not service.inventory.movements
    dispatched = await service.dispatch(transfer.id, tenant_id=tenant_id, active_branch_id=source_branch_id, actor_id=None)
    received = await service.receive(transfer.id, tenant_id=tenant_id, active_branch_id=target_branch_id, actor_id=None)

    assert dispatched.status == InventoryTransferStatus.RECEIVED
    assert received.inbound_movement_id is not None
    assert [movement.movement_type for movement in service.inventory.movements] == [
        InventoryMovementType.TRANSFER_OUT,
        InventoryMovementType.TRANSFER_IN,
    ]
    assert service.inventory.balances[(source_branch_id, source_warehouse_id, None)].physical_quantity == Decimal("7.000")
    assert service.inventory.balances[(target_branch_id, target_warehouse_id, None)].physical_quantity == Decimal("3.000")


@pytest.mark.asyncio
async def test_transfer_cannot_dispatch_reserved_or_missing_stock() -> None:
    tenant_id, product_id = uuid4(), uuid4()
    source_branch_id, target_branch_id = uuid4(), uuid4()
    source_warehouse_id, target_warehouse_id = uuid4(), uuid4()
    service = _service(tenant_id, source_branch_id, source_warehouse_id, product_id, target_branch_id, target_warehouse_id)
    transfer = await service.create(InventoryTransferCreateInput(
        tenant_id=tenant_id, source_branch_id=source_branch_id, source_warehouse_id=source_warehouse_id,
        target_branch_id=target_branch_id, target_warehouse_id=target_warehouse_id, product_id=product_id,
        quantity=Decimal(11), code="TRF-002", reason="Reposição da filial",
    ))

    with pytest.raises(InventoryInsufficientStockError):
        await service.dispatch(transfer.id, tenant_id=tenant_id, active_branch_id=source_branch_id, actor_id=None)

    assert not service.inventory.movements
