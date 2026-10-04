from dataclasses import dataclass
from decimal import Decimal
from secrets import token_urlsafe
from uuid import UUID

from app.modules.restaurant.domain.entities import RestaurantTableShape, RestaurantTableStatus
from app.modules.restaurant.domain.exceptions import (
    RestaurantBranchRequiredError,
    RestaurantFloorCodeAlreadyExistsError,
    RestaurantFloorNotFoundError,
    RestaurantInvalidDataError,
    RestaurantTableNotFoundError,
    RestaurantTableNumberAlreadyExistsError,
)
from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantTableRepository,
)
from app.modules.restaurant.infrastructure.models import RestaurantFloorModel, RestaurantTableModel


@dataclass(frozen=True)
class FloorInput:
    tenant_id: UUID
    branch_id: UUID | None
    code: str
    name: str
    description: str | None = None
    sort_order: int = 0
    is_active: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class TableInput:
    tenant_id: UUID
    branch_id: UUID | None
    floor_id: UUID
    number: str
    name: str | None = None
    capacity: int = 2
    position_x: Decimal = Decimal(0)
    position_y: Decimal = Decimal(0)
    width: Decimal = Decimal(96)
    height: Decimal = Decimal(72)
    shape: RestaurantTableShape = RestaurantTableShape.SQUARE
    status: RestaurantTableStatus = RestaurantTableStatus.AVAILABLE
    qr_code: str | None = None
    sort_order: int = 0
    is_active: bool = True
    actor_id: UUID | None = None


def _required_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise RestaurantBranchRequiredError("Active branch is required.")
    return branch_id


def _text(value: str, field: str, *, max_length: int) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > max_length:
        raise RestaurantInvalidDataError(f"Invalid {field}.")
    return normalized


def _optional_text(value: str | None, field: str, *, max_length: int) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) > max_length:
        raise RestaurantInvalidDataError(f"Invalid {field}.")
    return normalized


async def _floor(
    floors: RestaurantFloorRepository, floor_id: UUID, tenant_id: UUID, branch_id: UUID
) -> RestaurantFloorModel:
    floor = await floors.get_by_id(floor_id, tenant_id=tenant_id)
    if floor is None or floor.branch_id != branch_id:
        raise RestaurantFloorNotFoundError("Restaurant floor not found.")
    return floor


class CreateRestaurantFloor:
    def __init__(self, floors: RestaurantFloorRepository) -> None:
        self.floors = floors

    async def execute(self, data: FloorInput) -> RestaurantFloorModel:
        branch_id = _required_branch(data.branch_id)
        code = _text(data.code, "code", max_length=40).upper()
        if await self.floors.exists_by_code(code, tenant_id=data.tenant_id, branch_id=branch_id):
            raise RestaurantFloorCodeAlreadyExistsError("Restaurant floor code already exists.")
        return await self.floors.add(
            RestaurantFloorModel(
                tenant_id=data.tenant_id,
                branch_id=branch_id,
                code=code,
                name=_text(data.name, "name", max_length=120),
                description=_optional_text(data.description, "description", max_length=2000),
                sort_order=data.sort_order,
                is_active=data.is_active,
                created_by=data.actor_id,
                updated_by=data.actor_id,
            )
        )


class ListRestaurantFloors:
    def __init__(self, floors: RestaurantFloorRepository) -> None:
        self.floors = floors

    async def execute(
        self, *, tenant_id: UUID, branch_id: UUID | None, is_active: bool | None
    ) -> list[RestaurantFloorModel]:
        return await self.floors.list(
            tenant_id=tenant_id, branch_id=_required_branch(branch_id), is_active=is_active
        )


class GetRestaurantFloor:
    def __init__(self, floors: RestaurantFloorRepository) -> None:
        self.floors = floors

    async def execute(self, floor_id: UUID, *, tenant_id: UUID) -> RestaurantFloorModel:
        floor = await self.floors.get_by_id(floor_id, tenant_id=tenant_id)
        if floor is None:
            raise RestaurantFloorNotFoundError("Restaurant floor not found.")
        return floor


class UpdateRestaurantFloor:
    def __init__(self, floors: RestaurantFloorRepository) -> None:
        self.floors = floors

    async def execute(self, floor_id: UUID, data: FloorInput) -> RestaurantFloorModel:
        floor = await _floor(
            self.floors, floor_id, data.tenant_id, _required_branch(data.branch_id)
        )
        code = _text(data.code, "code", max_length=40).upper()
        if await self.floors.exists_by_code(
            code, tenant_id=data.tenant_id, branch_id=floor.branch_id, exclude_id=floor.id
        ):
            raise RestaurantFloorCodeAlreadyExistsError("Restaurant floor code already exists.")
        floor.code, floor.name = code, _text(data.name, "name", max_length=120)
        floor.description = _optional_text(data.description, "description", max_length=2000)
        floor.sort_order, floor.is_active, floor.updated_by = (
            data.sort_order,
            data.is_active,
            data.actor_id,
        )
        return await self.floors.add(floor)


class DeleteRestaurantFloor:
    def __init__(self, floors: RestaurantFloorRepository) -> None:
        self.floors = floors

    async def execute(
        self, floor_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantFloorModel:
        floor = await GetRestaurantFloor(self.floors).execute(floor_id, tenant_id=tenant_id)
        floor.is_active, floor.deleted_by, floor.updated_by = False, actor_id, actor_id
        floor.mark_as_deleted()
        return await self.floors.add(floor)


class CreateRestaurantTable:
    def __init__(
        self, floors: RestaurantFloorRepository, tables: RestaurantTableRepository
    ) -> None:
        self.floors, self.tables = floors, tables

    async def execute(self, data: TableInput) -> RestaurantTableModel:
        branch_id = _required_branch(data.branch_id)
        await _floor(self.floors, data.floor_id, data.tenant_id, branch_id)
        number = _text(data.number, "number", max_length=40).upper()
        if data.capacity < 1 or data.width <= 0 or data.height <= 0:
            raise RestaurantInvalidDataError("Invalid restaurant table dimensions.")
        if await self.tables.exists_by_number(
            number, tenant_id=data.tenant_id, floor_id=data.floor_id
        ):
            raise RestaurantTableNumberAlreadyExistsError("Restaurant table number already exists.")
        return await self.tables.add(
            RestaurantTableModel(
                tenant_id=data.tenant_id,
                branch_id=branch_id,
                floor_id=data.floor_id,
                number=number,
                name=_optional_text(data.name, "name", max_length=120),
                capacity=data.capacity,
                position_x=data.position_x,
                position_y=data.position_y,
                width=data.width,
                height=data.height,
                shape=data.shape,
                status=data.status if data.is_active else RestaurantTableStatus.BLOCKED,
                qr_code=_optional_text(data.qr_code, "qr_code", max_length=160),
                sort_order=data.sort_order,
                is_active=data.is_active,
                created_by=data.actor_id,
                updated_by=data.actor_id,
            )
        )


class ListRestaurantTables:
    def __init__(self, tables: RestaurantTableRepository) -> None:
        self.tables = tables

    async def execute(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        floor_id: UUID | None,
        is_active: bool | None,
    ) -> list[RestaurantTableModel]:
        return await self.tables.list(
            tenant_id=tenant_id,
            branch_id=_required_branch(branch_id),
            floor_id=floor_id,
            is_active=is_active,
        )


class GetRestaurantTable:
    def __init__(self, tables: RestaurantTableRepository) -> None:
        self.tables = tables

    async def execute(self, table_id: UUID, *, tenant_id: UUID) -> RestaurantTableModel:
        table = await self.tables.get_by_id(table_id, tenant_id=tenant_id)
        if table is None:
            raise RestaurantTableNotFoundError("Restaurant table not found.")
        return table


class GetRestaurantTableByQrCode:
    def __init__(self, tables: RestaurantTableRepository) -> None:
        self.tables = tables

    async def execute(self, qr_code: str) -> RestaurantTableModel:
        table = await self.tables.get_by_qr_code(qr_code)
        if table is None:
            raise RestaurantTableNotFoundError("Restaurant table not found.")
        return table


class UpdateRestaurantTable:
    def __init__(
        self, floors: RestaurantFloorRepository, tables: RestaurantTableRepository
    ) -> None:
        self.floors, self.tables = floors, tables

    async def execute(self, table_id: UUID, data: TableInput) -> RestaurantTableModel:
        branch_id = _required_branch(data.branch_id)
        table = await GetRestaurantTable(self.tables).execute(table_id, tenant_id=data.tenant_id)
        await _floor(self.floors, data.floor_id, data.tenant_id, branch_id)
        number = _text(data.number, "number", max_length=40).upper()
        if data.capacity < 1 or data.width <= 0 or data.height <= 0:
            raise RestaurantInvalidDataError("Invalid restaurant table dimensions.")
        if await self.tables.exists_by_number(
            number, tenant_id=data.tenant_id, floor_id=data.floor_id, exclude_id=table.id
        ):
            raise RestaurantTableNumberAlreadyExistsError("Restaurant table number already exists.")
        table.floor_id, table.number, table.name, table.capacity = (
            data.floor_id,
            number,
            _optional_text(data.name, "name", max_length=120),
            data.capacity,
        )
        table.position_x, table.position_y, table.width, table.height = (
            data.position_x,
            data.position_y,
            data.width,
            data.height,
        )
        table.shape, table.status = (
            data.shape,
            data.status if data.is_active else RestaurantTableStatus.BLOCKED,
        )
        table.qr_code, table.sort_order, table.is_active, table.updated_by = (
            _optional_text(data.qr_code, "qr_code", max_length=160),
            data.sort_order,
            data.is_active,
            data.actor_id,
        )
        return await self.tables.add(table)


class DeleteRestaurantTable:
    def __init__(self, tables: RestaurantTableRepository) -> None:
        self.tables = tables

    async def execute(
        self, table_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantTableModel:
        table = await GetRestaurantTable(self.tables).execute(table_id, tenant_id=tenant_id)
        table.deactivate()
        table.mark_as_deleted()
        table.deleted_by = actor_id
        table.updated_by = actor_id
        return await self.tables.add(table)


class GenerateRestaurantTableQr:
    def __init__(self, tables: RestaurantTableRepository) -> None:
        self.tables = tables

    async def execute(
        self, table_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantTableModel:
        table = await GetRestaurantTable(self.tables).execute(table_id, tenant_id=tenant_id)
        if not table.is_active:
            raise RestaurantInvalidDataError("An inactive table cannot receive a QR code.")
        table.qr_code = token_urlsafe(32)
        table.updated_by = actor_id
        return await self.tables.add(table)
