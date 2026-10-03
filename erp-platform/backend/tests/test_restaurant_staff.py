from uuid import uuid4

import pytest

from app.modules.restaurant.application.staff_use_cases import CreateRestaurantStaff, StaffInput
from app.modules.restaurant.domain.entities import RestaurantStaffRole, RestaurantStaffStatus
from app.modules.restaurant.domain.exceptions import RestaurantStaffCodeAlreadyExistsError
from app.modules.restaurant.domain.repositories import (
    RestaurantSectorRepository,
    RestaurantStaffRepository,
)


@pytest.mark.asyncio
async def test_staff_code_is_unique_inside_the_same_branch() -> None:
    staff = _Staff()
    sectors = _Sectors()
    input_data = StaffInput(
        tenant_id=uuid4(),
        branch_id=uuid4(),
        code="JOAO",
        name="João Silva",
        role=RestaurantStaffRole.WAITER,
        status=RestaurantStaffStatus.AVAILABLE,
    )
    created = await CreateRestaurantStaff(staff, sectors).execute(input_data)
    assert created.name == "João Silva"
    with pytest.raises(RestaurantStaffCodeAlreadyExistsError):
        await CreateRestaurantStaff(staff, sectors).execute(input_data)


class _Sectors(RestaurantSectorRepository):
    async def add(self, item):
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        return None

    async def list(self, **kwargs):
        return []

    async def exists_by_code(self, code, *, tenant_id, branch_id, exclude_id=None):
        return False


class _Staff(RestaurantStaffRepository):
    def __init__(self):
        self.items = {}

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
