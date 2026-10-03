from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.warehouse_location_use_cases import (
    ActivateWarehouseLocation,
    CreateWarehouseLocation,
    DeleteWarehouseLocation,
    WarehouseLocationCreateInput,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseLocationCodeAlreadyExistsError,
    WarehouseZoneNotFoundError,
)
from app.modules.inventory.domain.warehouse_location_repositories import (
    WarehouseLocationRepository,
)
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.domain.warehouse_zone_repositories import WarehouseZoneRepository
from app.modules.inventory.infrastructure.models import (
    WarehouseLocationModel,
    WarehouseModel,
    WarehouseZoneModel,
)


@pytest.mark.asyncio
async def test_create_warehouse_location_normalizes_code_and_sets_flags() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    zone = _zone(tenant_id, branch_id, warehouse.id)
    locations = _FakeWarehouseLocationRepository()

    location = await CreateWarehouseLocation(
        locations,
        _FakeWarehouseRepository([warehouse]),
        _FakeWarehouseZoneRepository([zone]),
    ).execute(
        WarehouseLocationCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            zone_id=zone.id,
            code=" a-01 ",
            name="Prateleira A01",
            barcode="BAR-A01",
            qr_code="rigaud://loc/a01",
            is_pick_location=True,
            sort_order=10,
        )
    )

    assert location.code == "A-01"
    assert location.warehouse_id == warehouse.id
    assert location.zone_id == zone.id
    assert location.branch_id == branch_id
    assert location.is_pick_location is True
    assert location.sort_order == 10


@pytest.mark.asyncio
async def test_create_warehouse_location_rejects_duplicate_code_in_same_warehouse() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    zone = _zone(tenant_id, branch_id, warehouse.id)
    locations = _FakeWarehouseLocationRepository()
    use_case = CreateWarehouseLocation(
        locations,
        _FakeWarehouseRepository([warehouse]),
        _FakeWarehouseZoneRepository([zone]),
    )
    await use_case.execute(
        WarehouseLocationCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            zone_id=zone.id,
            code="A-01",
            name="Prateleira A01",
        )
    )

    with pytest.raises(WarehouseLocationCodeAlreadyExistsError):
        await use_case.execute(
            WarehouseLocationCreateInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse.id,
                zone_id=zone.id,
                code=" a-01 ",
                name="Duplicada",
            )
        )


@pytest.mark.asyncio
async def test_create_warehouse_location_rejects_warehouse_from_another_branch() -> None:
    tenant_id = uuid4()
    warehouse = _warehouse(tenant_id, uuid4())
    zone = _zone(tenant_id, warehouse.branch_id, warehouse.id)

    with pytest.raises(WarehouseBranchRequiredError):
        await CreateWarehouseLocation(
            _FakeWarehouseLocationRepository(),
            _FakeWarehouseRepository([warehouse]),
            _FakeWarehouseZoneRepository([zone]),
        ).execute(
            WarehouseLocationCreateInput(
                tenant_id=tenant_id,
                branch_id=uuid4(),
                warehouse_id=warehouse.id,
                zone_id=zone.id,
                code="A-01",
                name="Prateleira A01",
            )
        )


@pytest.mark.asyncio
async def test_create_warehouse_location_rejects_zone_from_another_warehouse() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    warehouse = _warehouse(tenant_id, branch_id)
    zone = _zone(tenant_id, branch_id, uuid4())

    with pytest.raises(WarehouseZoneNotFoundError):
        await CreateWarehouseLocation(
            _FakeWarehouseLocationRepository(),
            _FakeWarehouseRepository([warehouse]),
            _FakeWarehouseZoneRepository([zone]),
        ).execute(
            WarehouseLocationCreateInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                warehouse_id=warehouse.id,
                zone_id=zone.id,
                code="A-01",
                name="Prateleira A01",
            )
        )


@pytest.mark.asyncio
async def test_delete_warehouse_location_marks_soft_deleted() -> None:
    tenant_id = uuid4()
    location = WarehouseLocationModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=uuid4(),
        warehouse_id=uuid4(),
        zone_id=uuid4(),
        code="A-01",
        name="Prateleira A01",
    )
    locations = _FakeWarehouseLocationRepository([location])

    deleted = await DeleteWarehouseLocation(locations).execute(
        location.id,
        tenant_id=tenant_id,
        actor_id=uuid4(),
    )

    assert deleted.deleted_at is not None
    assert deleted.is_active is False


@pytest.mark.asyncio
async def test_activate_warehouse_location_sets_active_status() -> None:
    tenant_id = uuid4()
    location = WarehouseLocationModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=uuid4(),
        warehouse_id=uuid4(),
        zone_id=uuid4(),
        code="A-01",
        name="Prateleira A01",
        is_active=False,
    )
    location.deactivate()
    locations = _FakeWarehouseLocationRepository([location])

    activated = await ActivateWarehouseLocation(locations).execute(
        location.id,
        tenant_id=tenant_id,
        actor_id=uuid4(),
    )

    assert activated.is_active is True


def _warehouse(tenant_id: UUID, branch_id: UUID) -> WarehouseModel:
    return WarehouseModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        code="MAIN",
        name="Deposito Principal",
        is_active=True,
    )


def _zone(tenant_id: UUID, branch_id: UUID, warehouse_id: UUID) -> WarehouseZoneModel:
    return WarehouseZoneModel(
        id=uuid4(),
        tenant_id=tenant_id,
        branch_id=branch_id,
        warehouse_id=warehouse_id,
        code="ALM",
        name="Almoxarifado",
        is_active=True,
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
        return []

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        return 0

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        warehouse_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return False


class _FakeWarehouseLocationRepository(WarehouseLocationRepository):
    def __init__(self, items: list[WarehouseLocationModel] | None = None) -> None:
        self.items: dict[UUID, WarehouseLocationModel] = {item.id: item for item in items or []}

    async def add(self, location: WarehouseLocationModel) -> WarehouseLocationModel:
        if location.id is None:
            location.id = uuid4()
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
        return []

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
        return 0

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

    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return any(
            item.barcode == barcode
            and item.tenant_id == tenant_id
            and item.deleted_at is None
            and item.id != exclude_id
            for item in self.items.values()
        )

    async def exists_by_qr_code(
        self,
        qr_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return any(
            item.qr_code == qr_code
            and item.tenant_id == tenant_id
            and item.deleted_at is None
            and item.id != exclude_id
            for item in self.items.values()
        )
