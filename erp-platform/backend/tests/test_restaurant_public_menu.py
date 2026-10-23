from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from app.modules.products.domain.entities import ProductStatus, ProductType, UnitOfMeasure
from app.modules.products.infrastructure.models import ProductModel
from app.modules.restaurant.application.public_menu_use_cases import GetRestaurantPublicMenu
from app.modules.restaurant.domain.entities import (
    RestaurantMenuAvailabilityStatus,
    RestaurantTableStatus,
)
from app.modules.restaurant.domain.exceptions import RestaurantTableNotFoundError
from app.modules.restaurant.domain.repositories import (
    RestaurantPublicMenuRepository,
    RestaurantTableRepository,
)
from app.modules.restaurant.infrastructure.models import (
    RestaurantMenuAvailabilityModel,
    RestaurantTableModel,
)


@pytest.mark.asyncio
async def test_public_menu_contains_only_published_qr_items_and_hides_internal_fields() -> None:
    tenant_id, branch_id, floor_id = uuid4(), uuid4(), uuid4()
    table = _table(tenant_id, branch_id, floor_id)
    published = _availability(tenant_id, branch_id, channels=["qr"])
    not_published_to_qr = _availability(tenant_id, branch_id, channels=["dining_room"])
    not_published = _availability(
        tenant_id,
        branch_id,
        status=RestaurantMenuAvailabilityStatus.UNAVAILABLE,
    )
    sold_out = _availability(tenant_id, branch_id, sold_quantity=2)
    inactive_product = _availability(tenant_id, branch_id)
    repository = _PublicMenuRepository(
        [
            (published, _product(tenant_id, name="Prato do dia")),
            (not_published_to_qr, _product(tenant_id, name="Prato interno")),
            (not_published, _product(tenant_id, name="Prato pausado")),
            (sold_out, _product(tenant_id, name="Prato esgotado")),
            (
                inactive_product,
                _product(tenant_id, name="Produto desativado", status=ProductStatus.INACTIVE),
            ),
        ]
    )

    menu = await GetRestaurantPublicMenu(
        _TableRepository(table),
        repository,
        clock=lambda: datetime(2026, 10, 13, 2, tzinfo=UTC),
    ).execute("active-qr-token")

    assert menu.table_number == "01"
    assert menu.restaurant_name == "Restaurante de teste"
    assert menu.currency == "BRL"
    assert menu.service_date == date(2026, 10, 12)
    assert {item.name for item in menu.items} == {"Prato do dia", "Prato esgotado"}
    sold_out_item = next(item for item in menu.items if item.name == "Prato esgotado")
    assert sold_out_item.is_available is False
    assert not hasattr(sold_out_item, "cost_price")
    assert repository.requested_scope == (tenant_id, branch_id, menu.service_date)


@pytest.mark.asyncio
async def test_public_menu_rejects_blocked_table_without_querying_availability() -> None:
    tenant_id, branch_id, floor_id = uuid4(), uuid4(), uuid4()
    table = _table(tenant_id, branch_id, floor_id, status=RestaurantTableStatus.BLOCKED)
    repository = _PublicMenuRepository([])

    with pytest.raises(RestaurantTableNotFoundError):
        await GetRestaurantPublicMenu(_TableRepository(table), repository).execute(
            "active-qr-token"
        )

    assert repository.requested_scope is None


@pytest.mark.asyncio
async def test_public_menu_rejects_table_when_branch_is_inactive() -> None:
    tenant_id, branch_id, floor_id = uuid4(), uuid4(), uuid4()
    table = _table(tenant_id, branch_id, floor_id)
    repository = _PublicMenuRepository([], branch_context=None)

    with pytest.raises(RestaurantTableNotFoundError):
        await GetRestaurantPublicMenu(_TableRepository(table), repository).execute(
            "active-qr-token"
        )


def _table(
    tenant_id,
    branch_id,
    floor_id,
    *,
    status=RestaurantTableStatus.AVAILABLE,
) -> RestaurantTableModel:
    return RestaurantTableModel(
        tenant_id=tenant_id,
        branch_id=branch_id,
        floor_id=floor_id,
        number="01",
        capacity=4,
        status=status,
        qr_code="active-qr-token",
        is_active=True,
        deleted_at=None,
    )


def _availability(
    tenant_id,
    branch_id,
    *,
    channels=None,
    status=RestaurantMenuAvailabilityStatus.PUBLISHED,
    sold_quantity=0,
) -> RestaurantMenuAvailabilityModel:
    return RestaurantMenuAvailabilityModel(
        tenant_id=tenant_id,
        branch_id=branch_id,
        product_id=uuid4(),
        service_date=date.today(),
        service_period="lunch",
        channels=channels if channels is not None else ["qr"],
        available_quantity=2,
        sold_quantity=sold_quantity,
        status=status,
        is_active=True,
        deleted_at=None,
    )


def _product(tenant_id, *, name: str, status=ProductStatus.ACTIVE) -> ProductModel:
    return ProductModel(
        tenant_id=tenant_id,
        name=name,
        internal_code="PRATO-001",
        product_type=ProductType.PREPARED_ITEM,
        unit_of_measure=UnitOfMeasure.PORTION,
        status=status,
        sale_price=Decimal("29.90"),
        cost_price=Decimal("10.00"),
        main_image_url="https://images.example.test/dish.jpg",
        is_active=True,
        is_available_for_sale=True,
        deleted_at=None,
    )


class _TableRepository(RestaurantTableRepository):
    def __init__(self, table: RestaurantTableModel) -> None:
        self.table = table

    async def add(self, item):
        return item

    async def get_by_id(self, item_id, *, tenant_id):
        return None

    async def get_by_qr_code(self, qr_code):
        return self.table if qr_code == self.table.qr_code else None

    async def list(self, **kwargs):
        return [self.table]

    async def exists_by_number(self, **kwargs):
        return False


class _PublicMenuRepository(RestaurantPublicMenuRepository):
    def __init__(
        self, items, *, branch_context=("America/Sao_Paulo", "BRL", "Restaurante de teste")
    ):
        self.items = items
        self.branch_context = branch_context
        self.requested_scope = None

    async def active_branch_context(self, *, tenant_id, branch_id):
        return self.branch_context

    async def list_published_items(self, *, tenant_id, branch_id, service_date):
        self.requested_scope = (tenant_id, branch_id, service_date)
        return self.items
