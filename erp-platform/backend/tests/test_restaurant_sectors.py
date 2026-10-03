from uuid import uuid4

import pytest

from app.modules.restaurant.application.sector_use_cases import (
    CreateRestaurantSector,
    SectorInput,
    UpdateRestaurantSector,
)
from app.modules.restaurant.domain.entities import RestaurantSectorType
from app.modules.restaurant.domain.exceptions import RestaurantSectorCodeAlreadyExistsError
from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantSectorRepository,
)


@pytest.mark.asyncio
async def test_sector_code_is_unique_inside_the_same_branch() -> None:
    tenant_id, branch_id = uuid4(), uuid4()
    sectors = _Sectors()
    floors = _Floors()
    input_data = SectorInput(
        tenant_id=tenant_id,
        branch_id=branch_id,
        code="SALA",
        name="Salão principal",
        type=RestaurantSectorType.DINING_ROOM,
    )

    created = await CreateRestaurantSector(sectors, floors).execute(input_data)

    assert created.code == "SALA"
    with pytest.raises(RestaurantSectorCodeAlreadyExistsError):
        await CreateRestaurantSector(sectors, floors).execute(input_data)


@pytest.mark.asyncio
async def test_sector_can_be_updated_without_conflicting_with_itself() -> None:
    tenant_id, branch_id = uuid4(), uuid4()
    sectors = _Sectors()
    floors = _Floors()
    created = await CreateRestaurantSector(sectors, floors).execute(
        SectorInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code="BAR",
            name="Bar",
            type=RestaurantSectorType.BAR,
        )
    )

    updated = await UpdateRestaurantSector(sectors, floors).execute(
        created.id,
        SectorInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code="BAR",
            name="Bar central",
            type=RestaurantSectorType.BAR,
        ),
    )

    assert updated.name == "Bar central"


class _Floors(RestaurantFloorRepository):
    async def add(self, item):
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        return None

    async def list(self, **kwargs):
        return []

    async def exists_by_code(self, code, *, tenant_id, branch_id, exclude_id=None):
        return False


class _Sectors(RestaurantSectorRepository):
    def __init__(self) -> None:
        self.items: dict = {}

    async def add(self, item):
        if item.id is None:
            item.id = uuid4()
        self.items[item.id] = item
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        item = self.items.get(item_id)
        if item is None or item.tenant_id != tenant_id or item.deleted_at is not None:
            return None
        return item

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
