from uuid import uuid4

import pytest

from app.modules.restaurant.application.table_use_cases import (
    CreateRestaurantFloor,
    CreateRestaurantTable,
    FloorInput,
    TableInput,
)
from app.modules.restaurant.domain.exceptions import RestaurantTableNumberAlreadyExistsError
from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantTableRepository,
)


@pytest.mark.asyncio
async def test_table_number_is_unique_inside_the_same_floor() -> None:
    tenant_id, branch_id = uuid4(), uuid4()
    floors, tables = _Floors(), _Tables()
    floor = await CreateRestaurantFloor(floors).execute(
        FloorInput(tenant_id=tenant_id, branch_id=branch_id, code="SALAO", name="Salão")
    )
    table_input = TableInput(
        tenant_id=tenant_id, branch_id=branch_id, floor_id=floor.id, number="01", capacity=4
    )
    created = await CreateRestaurantTable(floors, tables).execute(table_input)
    assert created.number == "01"
    with pytest.raises(RestaurantTableNumberAlreadyExistsError):
        await CreateRestaurantTable(floors, tables).execute(table_input)


class _Floors(RestaurantFloorRepository):
    def __init__(self) -> None:
        self.items: dict = {}

    async def add(self, item):
        if item.id is None:
            item.id = uuid4()
        self.items[item.id] = item
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        item = self.items.get(item_id)
        return item if item and item.tenant_id == tenant_id and item.deleted_at is None else None

    async def list(self, **kwargs):
        return list(self.items.values())

    async def exists_by_code(self, code, *, tenant_id, branch_id, exclude_id=None):
        return any(
            item.code == code
            and item.tenant_id == tenant_id
            and item.branch_id == branch_id
            and item.id != exclude_id
            and item.deleted_at is None
            for item in self.items.values()
        )


class _Tables(RestaurantTableRepository):
    def __init__(self) -> None:
        self.items: dict = {}

    async def add(self, item):
        if item.id is None:
            item.id = uuid4()
        self.items[item.id] = item
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        item = self.items.get(item_id)
        return item if item and item.tenant_id == tenant_id and item.deleted_at is None else None

    async def list(self, **kwargs):
        return list(self.items.values())

    async def exists_by_number(self, number, *, tenant_id, floor_id, exclude_id=None):
        return any(
            item.number == number
            and item.tenant_id == tenant_id
            and item.floor_id == floor_id
            and item.id != exclude_id
            and item.deleted_at is None
            for item in self.items.values()
        )
