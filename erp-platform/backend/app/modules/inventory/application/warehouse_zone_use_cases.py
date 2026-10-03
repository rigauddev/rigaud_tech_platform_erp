from dataclasses import dataclass
from uuid import UUID

from app.modules.inventory.application.validators import (
    normalize_optional_warehouse_zone_text,
    normalize_sort_order,
    normalize_warehouse_zone_code,
    normalize_warehouse_zone_text,
)
from app.modules.inventory.domain.entities import WarehouseZoneType
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseInactiveError,
    WarehouseNotFoundError,
    WarehouseZoneBranchRequiredError,
    WarehouseZoneCodeAlreadyExistsError,
    WarehouseZoneNotFoundError,
)
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.domain.warehouse_zone_repositories import WarehouseZoneRepository
from app.modules.inventory.infrastructure.models import WarehouseModel, WarehouseZoneModel


@dataclass(frozen=True)
class WarehouseZoneCreateInput:
    tenant_id: UUID
    branch_id: UUID | None
    warehouse_id: UUID
    code: str
    name: str
    description: str | None = None
    type: WarehouseZoneType = WarehouseZoneType.STORAGE
    color: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    is_receiving: bool = False
    is_shipping: bool = False
    is_storage: bool = True
    is_production: bool = False
    is_quarantine: bool = False
    is_active: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseZoneUpdateInput:
    code: str | None = None
    name: str | None = None
    description: str | None = None
    type: WarehouseZoneType | None = None
    color: str | None = None
    icon: str | None = None
    sort_order: int | None = None
    is_receiving: bool | None = None
    is_shipping: bool | None = None
    is_storage: bool | None = None
    is_production: bool | None = None
    is_quarantine: bool | None = None
    is_active: bool | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseZoneListInput:
    tenant_id: UUID
    branch_id: UUID | None = None
    warehouse_id: UUID | None = None
    is_active: bool | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class WarehouseZoneReorderInput:
    sort_order: int
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseZoneListResult:
    items: list[WarehouseZoneModel]
    total: int
    page: int
    page_size: int


class CreateWarehouseZone:
    def __init__(
        self,
        zones: WarehouseZoneRepository,
        warehouses: WarehouseRepository,
    ) -> None:
        self.zones = zones
        self.warehouses = warehouses

    async def execute(self, input_data: WarehouseZoneCreateInput) -> WarehouseZoneModel:
        branch_id = _require_branch(input_data.branch_id)
        warehouse = await _get_active_warehouse(
            self.warehouses,
            input_data.warehouse_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        )
        code = normalize_warehouse_zone_code(input_data.code)
        if await self.zones.exists_by_code(
            code,
            tenant_id=input_data.tenant_id,
            warehouse_id=warehouse.id,
        ):
            raise WarehouseZoneCodeAlreadyExistsError("Warehouse zone code already exists.")

        zone = WarehouseZoneModel(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            code=code,
            name=normalize_warehouse_zone_text(input_data.name, "name", max_length=120),
            description=normalize_optional_warehouse_zone_text(
                input_data.description, "description", max_length=500
            ),
            type=input_data.type,
            color=normalize_optional_warehouse_zone_text(input_data.color, "color", max_length=20),
            icon=normalize_optional_warehouse_zone_text(input_data.icon, "icon", max_length=80),
            sort_order=normalize_sort_order(input_data.sort_order),
            is_receiving=input_data.is_receiving,
            is_shipping=input_data.is_shipping,
            is_storage=input_data.is_storage,
            is_production=input_data.is_production,
            is_quarantine=input_data.is_quarantine,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        if input_data.is_active:
            zone.activate()
        else:
            zone.deactivate()
        return await self.zones.add(zone)


class ListWarehouseZones:
    def __init__(self, zones: WarehouseZoneRepository) -> None:
        self.zones = zones

    async def execute(self, input_data: WarehouseZoneListInput) -> WarehouseZoneListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        items = await self.zones.list(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            is_active=input_data.is_active,
            limit=page_size,
            offset=offset,
        )
        total = await self.zones.count(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            is_active=input_data.is_active,
        )
        return WarehouseZoneListResult(items=items, total=total, page=page, page_size=page_size)


class GetWarehouseZone:
    def __init__(self, zones: WarehouseZoneRepository) -> None:
        self.zones = zones

    async def execute(self, zone_id: UUID, *, tenant_id: UUID) -> WarehouseZoneModel:
        zone = await self.zones.get_by_id(zone_id, tenant_id=tenant_id)
        if zone is None:
            raise WarehouseZoneNotFoundError("Warehouse zone not found.")
        return zone


class UpdateWarehouseZone:
    def __init__(
        self,
        zones: WarehouseZoneRepository,
        warehouses: WarehouseRepository,
    ) -> None:
        self.zones = zones
        self.warehouses = warehouses

    async def execute(
        self,
        zone_id: UUID,
        *,
        tenant_id: UUID,
        input_data: WarehouseZoneUpdateInput,
    ) -> WarehouseZoneModel:
        zone = await GetWarehouseZone(self.zones).execute(zone_id, tenant_id=tenant_id)
        await _get_active_warehouse(
            self.warehouses,
            zone.warehouse_id,
            tenant_id=tenant_id,
            branch_id=zone.branch_id,
        )
        if input_data.code is not None:
            code = normalize_warehouse_zone_code(input_data.code)
            if await self.zones.exists_by_code(
                code,
                tenant_id=tenant_id,
                warehouse_id=zone.warehouse_id,
                exclude_id=zone.id,
            ):
                raise WarehouseZoneCodeAlreadyExistsError("Warehouse zone code already exists.")
            zone.code = code
        if input_data.name is not None:
            zone.name = normalize_warehouse_zone_text(input_data.name, "name", max_length=120)
        if input_data.description is not None:
            zone.description = normalize_optional_warehouse_zone_text(
                input_data.description, "description", max_length=500
            )
        if input_data.type is not None:
            zone.type = input_data.type
        if input_data.color is not None:
            zone.color = normalize_optional_warehouse_zone_text(
                input_data.color, "color", max_length=20
            )
        if input_data.icon is not None:
            zone.icon = normalize_optional_warehouse_zone_text(
                input_data.icon, "icon", max_length=80
            )
        if input_data.sort_order is not None:
            zone.sort_order = normalize_sort_order(input_data.sort_order)
        _apply_flags(zone, input_data)
        if input_data.is_active is not None:
            if input_data.is_active:
                zone.activate()
            else:
                zone.deactivate()
        zone.updated_by = input_data.actor_id
        return await self.zones.add(zone)


class ReorderWarehouseZone:
    def __init__(self, zones: WarehouseZoneRepository) -> None:
        self.zones = zones

    async def execute(
        self,
        zone_id: UUID,
        *,
        tenant_id: UUID,
        input_data: WarehouseZoneReorderInput,
    ) -> WarehouseZoneModel:
        zone = await GetWarehouseZone(self.zones).execute(zone_id, tenant_id=tenant_id)
        zone.sort_order = normalize_sort_order(input_data.sort_order)
        zone.updated_by = input_data.actor_id
        return await self.zones.add(zone)


class DeleteWarehouseZone:
    def __init__(self, zones: WarehouseZoneRepository) -> None:
        self.zones = zones

    async def execute(
        self,
        zone_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> WarehouseZoneModel:
        zone = await GetWarehouseZone(self.zones).execute(zone_id, tenant_id=tenant_id)
        zone.deactivate()
        zone.mark_as_deleted()
        zone.deleted_by = actor_id
        zone.updated_by = actor_id
        return await self.zones.add(zone)


def _require_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise WarehouseZoneBranchRequiredError("Active branch is required.")
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
        raise WarehouseBranchRequiredError("Warehouse branch does not match active branch.")
    if not warehouse.is_active:
        raise WarehouseInactiveError("Warehouse is inactive.")
    return warehouse


def _apply_flags(zone: WarehouseZoneModel, input_data: WarehouseZoneUpdateInput) -> None:
    if input_data.is_receiving is not None:
        zone.is_receiving = input_data.is_receiving
    if input_data.is_shipping is not None:
        zone.is_shipping = input_data.is_shipping
    if input_data.is_storage is not None:
        zone.is_storage = input_data.is_storage
    if input_data.is_production is not None:
        zone.is_production = input_data.is_production
    if input_data.is_quarantine is not None:
        zone.is_quarantine = input_data.is_quarantine
