from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.modules.inventory.application.validators import (
    normalize_location_capacity,
    normalize_location_sort_order,
    normalize_optional_warehouse_location_text,
    normalize_warehouse_location_code,
    normalize_warehouse_location_text,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseInactiveError,
    WarehouseLocationBarcodeAlreadyExistsError,
    WarehouseLocationBranchRequiredError,
    WarehouseLocationCodeAlreadyExistsError,
    WarehouseLocationNotFoundError,
    WarehouseLocationQrCodeAlreadyExistsError,
    WarehouseNotFoundError,
    WarehouseZoneInactiveError,
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


@dataclass(frozen=True)
class WarehouseLocationCreateInput:
    tenant_id: UUID
    branch_id: UUID | None
    warehouse_id: UUID
    zone_id: UUID
    code: str
    name: str
    alias: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    aisle: str | None = None
    rack: str | None = None
    shelf: str | None = None
    level: str | None = None
    position: str | None = None
    capacity: Decimal | str | int | None = None
    capacity_unit: str | None = None
    allow_negative: bool = False
    allow_mixed_items: bool = True
    allow_expired: bool = False
    is_pick_location: bool = False
    is_receive_location: bool = False
    is_shipping_location: bool = False
    is_default: bool = False
    sort_order: int | None = None
    is_active: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseLocationUpdateInput:
    code: str | None = None
    name: str | None = None
    alias: str | None = None
    barcode: str | None = None
    qr_code: str | None = None
    aisle: str | None = None
    rack: str | None = None
    shelf: str | None = None
    level: str | None = None
    position: str | None = None
    capacity: Decimal | str | int | None = None
    capacity_unit: str | None = None
    allow_negative: bool | None = None
    allow_mixed_items: bool | None = None
    allow_expired: bool | None = None
    is_pick_location: bool | None = None
    is_receive_location: bool | None = None
    is_shipping_location: bool | None = None
    is_default: bool | None = None
    sort_order: int | None = None
    is_active: bool | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseLocationListInput:
    tenant_id: UUID
    branch_id: UUID | None = None
    warehouse_id: UUID | None = None
    zone_id: UUID | None = None
    search: str | None = None
    is_active: bool | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class WarehouseLocationReorderInput:
    sort_order: int
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseLocationListResult:
    items: list[WarehouseLocationModel]
    total: int
    page: int
    page_size: int


class CreateWarehouseLocation:
    def __init__(
        self,
        locations: WarehouseLocationRepository,
        warehouses: WarehouseRepository,
        zones: WarehouseZoneRepository,
    ) -> None:
        self.locations = locations
        self.warehouses = warehouses
        self.zones = zones

    async def execute(self, input_data: WarehouseLocationCreateInput) -> WarehouseLocationModel:
        branch_id = _require_branch(input_data.branch_id)
        warehouse = await _get_active_warehouse(
            self.warehouses,
            input_data.warehouse_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        )
        zone = await _get_active_zone(
            self.zones,
            input_data.zone_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
        )
        code = normalize_warehouse_location_code(input_data.code)
        await _ensure_unique_values(
            self.locations,
            code=code,
            barcode=input_data.barcode,
            qr_code=input_data.qr_code,
            tenant_id=input_data.tenant_id,
            warehouse_id=warehouse.id,
        )
        location = WarehouseLocationModel(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            warehouse_id=warehouse.id,
            zone_id=zone.id,
            code=code,
            name=normalize_warehouse_location_text(input_data.name, "name", max_length=120),
            alias=normalize_optional_warehouse_location_text(
                input_data.alias, "alias", max_length=80
            ),
            barcode=normalize_optional_warehouse_location_text(
                input_data.barcode, "barcode", max_length=80
            ),
            qr_code=normalize_optional_warehouse_location_text(
                input_data.qr_code, "qr_code", max_length=160
            ),
            aisle=normalize_optional_warehouse_location_text(
                input_data.aisle, "aisle", max_length=40
            ),
            rack=normalize_optional_warehouse_location_text(input_data.rack, "rack", max_length=40),
            shelf=normalize_optional_warehouse_location_text(
                input_data.shelf, "shelf", max_length=40
            ),
            level=normalize_optional_warehouse_location_text(
                input_data.level, "level", max_length=40
            ),
            position=normalize_optional_warehouse_location_text(
                input_data.position, "position", max_length=40
            ),
            capacity=normalize_location_capacity(input_data.capacity),
            capacity_unit=normalize_optional_warehouse_location_text(
                input_data.capacity_unit, "capacity_unit", max_length=20
            ),
            allow_negative=input_data.allow_negative,
            allow_mixed_items=input_data.allow_mixed_items,
            allow_expired=input_data.allow_expired,
            is_pick_location=input_data.is_pick_location,
            is_receive_location=input_data.is_receive_location,
            is_shipping_location=input_data.is_shipping_location,
            is_default=input_data.is_default,
            sort_order=normalize_location_sort_order(input_data.sort_order),
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        if input_data.is_active:
            location.activate()
        else:
            location.deactivate()
        return await self.locations.add(location)


class ListWarehouseLocations:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(self, input_data: WarehouseLocationListInput) -> WarehouseLocationListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        items = await self.locations.list(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            zone_id=input_data.zone_id,
            search=search,
            is_active=input_data.is_active,
            limit=page_size,
            offset=offset,
        )
        total = await self.locations.count(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            warehouse_id=input_data.warehouse_id,
            zone_id=input_data.zone_id,
            search=search,
            is_active=input_data.is_active,
        )
        return WarehouseLocationListResult(items=items, total=total, page=page, page_size=page_size)


class GetWarehouseLocation:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(self, location_id: UUID, *, tenant_id: UUID) -> WarehouseLocationModel:
        location = await self.locations.get_by_id(location_id, tenant_id=tenant_id)
        if location is None:
            raise WarehouseLocationNotFoundError("Warehouse location not found.")
        return location


class UpdateWarehouseLocation:
    def __init__(
        self,
        locations: WarehouseLocationRepository,
        warehouses: WarehouseRepository,
        zones: WarehouseZoneRepository,
    ) -> None:
        self.locations = locations
        self.warehouses = warehouses
        self.zones = zones

    async def execute(
        self,
        location_id: UUID,
        *,
        tenant_id: UUID,
        input_data: WarehouseLocationUpdateInput,
    ) -> WarehouseLocationModel:
        location = await GetWarehouseLocation(self.locations).execute(
            location_id, tenant_id=tenant_id
        )
        await _get_active_warehouse(
            self.warehouses,
            location.warehouse_id,
            tenant_id=tenant_id,
            branch_id=location.branch_id,
        )
        await _get_active_zone(
            self.zones,
            location.zone_id,
            tenant_id=tenant_id,
            branch_id=location.branch_id,
            warehouse_id=location.warehouse_id,
        )
        code = location.code
        if input_data.code is not None:
            code = normalize_warehouse_location_code(input_data.code)
        await _ensure_unique_values(
            self.locations,
            code=code,
            barcode=input_data.barcode,
            qr_code=input_data.qr_code,
            tenant_id=tenant_id,
            warehouse_id=location.warehouse_id,
            exclude_id=location.id,
        )
        if input_data.code is not None:
            location.code = code
        _apply_text_updates(location, input_data)
        _apply_bool_updates(location, input_data)
        if input_data.capacity is not None:
            location.capacity = normalize_location_capacity(input_data.capacity)
        if input_data.sort_order is not None:
            location.sort_order = normalize_location_sort_order(input_data.sort_order)
        if input_data.is_active is not None:
            if input_data.is_active:
                location.activate()
            else:
                location.deactivate()
        location.updated_by = input_data.actor_id
        return await self.locations.add(location)


class ActivateWarehouseLocation:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(
        self, location_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> WarehouseLocationModel:
        location = await GetWarehouseLocation(self.locations).execute(
            location_id, tenant_id=tenant_id
        )
        location.activate()
        location.updated_by = actor_id
        return await self.locations.add(location)


class DeactivateWarehouseLocation:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(
        self, location_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> WarehouseLocationModel:
        location = await GetWarehouseLocation(self.locations).execute(
            location_id, tenant_id=tenant_id
        )
        location.deactivate()
        location.updated_by = actor_id
        return await self.locations.add(location)


class ReorderWarehouseLocation:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(
        self,
        location_id: UUID,
        *,
        tenant_id: UUID,
        input_data: WarehouseLocationReorderInput,
    ) -> WarehouseLocationModel:
        location = await GetWarehouseLocation(self.locations).execute(
            location_id, tenant_id=tenant_id
        )
        location.sort_order = normalize_location_sort_order(input_data.sort_order)
        location.updated_by = input_data.actor_id
        return await self.locations.add(location)


class DeleteWarehouseLocation:
    def __init__(self, locations: WarehouseLocationRepository) -> None:
        self.locations = locations

    async def execute(
        self,
        location_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None,
    ) -> WarehouseLocationModel:
        location = await GetWarehouseLocation(self.locations).execute(
            location_id, tenant_id=tenant_id
        )
        location.deactivate()
        location.mark_as_deleted()
        location.deleted_by = actor_id
        return await self.locations.add(location)


def _require_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise WarehouseLocationBranchRequiredError("Active branch is required.")
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


async def _get_active_zone(
    zones: WarehouseZoneRepository,
    zone_id: UUID,
    *,
    tenant_id: UUID,
    branch_id: UUID,
    warehouse_id: UUID,
) -> WarehouseZoneModel:
    zone = await zones.get_by_id(zone_id, tenant_id=tenant_id)
    if zone is None:
        raise WarehouseZoneNotFoundError("Warehouse zone not found.")
    if zone.branch_id != branch_id or zone.warehouse_id != warehouse_id:
        raise WarehouseZoneNotFoundError("Warehouse zone not found in warehouse.")
    if not zone.is_active:
        raise WarehouseZoneInactiveError("Warehouse zone is inactive.")
    return zone


async def _ensure_unique_values(
    locations: WarehouseLocationRepository,
    *,
    code: str,
    barcode: str | None,
    qr_code: str | None,
    tenant_id: UUID,
    warehouse_id: UUID,
    exclude_id: UUID | None = None,
) -> None:
    if await locations.exists_by_code(
        code,
        tenant_id=tenant_id,
        warehouse_id=warehouse_id,
        exclude_id=exclude_id,
    ):
        raise WarehouseLocationCodeAlreadyExistsError("Warehouse location code already exists.")
    normalized_barcode = normalize_optional_warehouse_location_text(
        barcode, "barcode", max_length=80
    )
    if normalized_barcode and await locations.exists_by_barcode(
        normalized_barcode, tenant_id=tenant_id, exclude_id=exclude_id
    ):
        raise WarehouseLocationBarcodeAlreadyExistsError("Warehouse location barcode exists.")
    normalized_qr_code = normalize_optional_warehouse_location_text(
        qr_code, "qr_code", max_length=160
    )
    if normalized_qr_code and await locations.exists_by_qr_code(
        normalized_qr_code, tenant_id=tenant_id, exclude_id=exclude_id
    ):
        raise WarehouseLocationQrCodeAlreadyExistsError("Warehouse location QR Code exists.")


def _apply_text_updates(
    location: WarehouseLocationModel,
    input_data: WarehouseLocationUpdateInput,
) -> None:
    fields = {
        "name": (input_data.name, 120, True),
        "alias": (input_data.alias, 80, False),
        "barcode": (input_data.barcode, 80, False),
        "qr_code": (input_data.qr_code, 160, False),
        "aisle": (input_data.aisle, 40, False),
        "rack": (input_data.rack, 40, False),
        "shelf": (input_data.shelf, 40, False),
        "level": (input_data.level, 40, False),
        "position": (input_data.position, 40, False),
        "capacity_unit": (input_data.capacity_unit, 20, False),
    }
    for field, (value, max_length, required) in fields.items():
        if value is None:
            continue
        normalized = (
            normalize_warehouse_location_text(value, field, max_length=max_length)
            if required
            else normalize_optional_warehouse_location_text(value, field, max_length=max_length)
        )
        setattr(location, field, normalized)


def _apply_bool_updates(
    location: WarehouseLocationModel,
    input_data: WarehouseLocationUpdateInput,
) -> None:
    for field in (
        "allow_negative",
        "allow_mixed_items",
        "allow_expired",
        "is_pick_location",
        "is_receive_location",
        "is_shipping_location",
        "is_default",
    ):
        value = getattr(input_data, field)
        if value is not None:
            setattr(location, field, value)
