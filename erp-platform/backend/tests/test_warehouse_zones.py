from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.warehouse_zone_use_cases import (
    CreateWarehouseZone,
    ReorderWarehouseZone,
    WarehouseZoneCreateInput,
    WarehouseZoneReorderInput,
)
from app.modules.inventory.domain.entities import WarehouseZoneType
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseZoneCodeAlreadyExistsError,
)
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.domain.warehouse_zone_repositories import WarehouseZoneRepository
from app.modules.inventory.infrastructure.models import WarehouseModel, WarehouseZoneModel


@pytest.mark.asyncio
async def test_create_warehouse_zone_normalizes_code_and_sets_flags() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = WarehouseModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        code="MAIN",
        name="Depósito Principal",
        is_active=True,
    )
    zones = _FakeWarehouseZoneRepository()
    warehouses = _FakeWarehouseRepository([warehouse])

    zone = await CreateWarehouseZone(zones, warehouses).execute(
        WarehouseZoneCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            code=" rec ",
            name="Recebimento",
            type=WarehouseZoneType.RECEIVING,
            is_receiving=True,
            is_storage=False,
            sort_order=10,
        )
    )

    assert zone.code == "REC"
    assert zone.warehouse_id == warehouse.id
    assert zone.branch_id == branch_id
    assert zone.type == WarehouseZoneType.RECEIVING
    assert zone.is_receiving is True
    assert zone.is_storage is False
    assert zone.sort_order == 10


@pytest.mark.asyncio
async def test_create_warehouse_zone_rejects_duplicate_code_in_same_warehouse() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = WarehouseModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        code="MAIN",
        name="Depósito Principal",
        is_active=True,
    )
    zones = _FakeWarehouseZoneRepository()
    warehouses = _FakeWarehouseRepository([warehouse])
    await CreateWarehouseZone(zones, warehouses).execute(
        WarehouseZoneCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            code="PICK",
            name="Picking",
        )
    )

    with pytest.raises(WarehouseZoneCodeAlreadyExistsError):
        await CreateWarehouseZone(zones, warehouses).execute(
            WarehouseZoneCreateInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse.id,
                code="pick",
                name="Picking duplicado",
            )
        )


@pytest.mark.asyncio
async def test_create_warehouse_zone_rejects_warehouse_from_another_branch() -> None:
    tenant_id = uuid4()
    warehouse = WarehouseModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=uuid4(),
        code="MAIN",
        name="Depósito Principal",
        is_active=True,
    )
    zones = _FakeWarehouseZoneRepository()
    warehouses = _FakeWarehouseRepository([warehouse])

    with pytest.raises(WarehouseBranchRequiredError):
        await CreateWarehouseZone(zones, warehouses).execute(
            WarehouseZoneCreateInput(
                tenant_id=tenant_id,
                branch_id=uuid4(),
                warehouse_id=warehouse.id,
                code="REC",
                name="Recebimento",
            )
        )


@pytest.mark.asyncio
async def test_reorder_warehouse_zone_updates_sort_order() -> None:
    tenant_id = uuid4()
    zone = WarehouseZoneModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=uuid4(),
        warehouse_id=uuid4(),
        code="PICK",
        name="Picking",
        sort_order=1,
    )
    zones = _FakeWarehouseZoneRepository([zone])

    updated = await ReorderWarehouseZone(zones).execute(
        zone.id,
        tenant_id=tenant_id,
        input_data=WarehouseZoneReorderInput(sort_order=30),
    )

    assert updated.sort_order == 30


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
        return []

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        return 0

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


class _FakeWarehouseZoneRepository(WarehouseZoneRepository):
    def __init__(self, items: list[WarehouseZoneModel] | None = None) -> None:
        self.items: dict[UUID, WarehouseZoneModel] = {item.id: item for item in items or []}

    async def add(self, zone: WarehouseZoneModel) -> WarehouseZoneModel:
        if zone.id is None:
            zone.id = uuid4()
        self.items[zone.id] = zone
        return zone

    async def get_by_id(self, zone_id: UUID, *, tenant_id: UUID) -> WarehouseZoneModel | None:
        zone = self.items.get(zone_id)
        if zone and zone.tenant_id == tenant_id and zone.deleted_at is None:
            return zone
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseZoneModel]:
        items = [
            item
            for item in self.items.values()
            if item.tenant_id == tenant_id
            and item.deleted_at is None
            and (branch_id is None or item.branch_id == branch_id)
            and (warehouse_id is None or item.warehouse_id == warehouse_id)
            and (is_active is None or item.is_active == is_active)
        ]
        return sorted(items, key=lambda item: (item.sort_order, item.name))[offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        return len(
            await self.list(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse_id,
                is_active=is_active,
                limit=100,
                offset=0,
            )
        )

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        warehouse_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return any(
            item.code == code
            and item.tenant_id == tenant_id
            and item.warehouse_id == warehouse_id
            and item.deleted_at is None
            and item.id != exclude_id
            for item in self.items.values()
        )
