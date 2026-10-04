from datetime import date
from uuid import uuid4

import pytest

from app.modules.restaurant.application.menu_availability_use_cases import (
    CreateRestaurantMenuAvailability,
    MenuAvailabilityInput,
)
from app.modules.restaurant.domain.entities import RestaurantMenuAvailabilityStatus
from app.modules.restaurant.domain.exceptions import RestaurantMenuAvailabilityAlreadyExistsError
from app.modules.restaurant.domain.repositories import RestaurantMenuAvailabilityRepository


@pytest.mark.asyncio
async def test_menu_item_is_unique_per_branch_date_and_service_period() -> None:
    repository = _MenuAvailabilityRepository()
    data = MenuAvailabilityInput(
        tenant_id=uuid4(),
        branch_id=uuid4(),
        product_id=uuid4(),
        service_date=date(2026, 10, 3),
        service_period="lunch",
        channels=["dining_room", "qr"],
        available_quantity=20,
        status=RestaurantMenuAvailabilityStatus.PUBLISHED,
        is_active=True,
    )
    created = await CreateRestaurantMenuAvailability(repository).execute(data)
    assert created.available_quantity == 20
    assert created.channels == ["dining_room", "qr"]
    with pytest.raises(RestaurantMenuAvailabilityAlreadyExistsError):
        await CreateRestaurantMenuAvailability(repository).execute(data)


class _MenuAvailabilityRepository(RestaurantMenuAvailabilityRepository):
    def __init__(self) -> None:
        self.items = []

    async def add(self, item):
        if item.id is None:
            item.id = uuid4()
        self.items.append(item)
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        return next((item for item in self.items if item.id == item_id), None)

    async def list(self, **kwargs):
        return self.items

    async def exists_in_scope(
        self, *, tenant_id, branch_id, product_id, service_date, service_period, exclude_id=None
    ):
        return any(
            item.tenant_id == tenant_id
            and item.branch_id == branch_id
            and item.product_id == product_id
            and item.service_date == service_date
            and item.service_period == service_period
            and item.id != exclude_id
            for item in self.items
        )

    async def product_exists(self, product_id, *, tenant_id):
        return True
