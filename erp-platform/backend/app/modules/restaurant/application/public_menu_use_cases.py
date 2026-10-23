from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.modules.products.domain.entities import ProductStatus
from app.modules.products.infrastructure.models import ProductModel
from app.modules.restaurant.application.table_use_cases import GetRestaurantTableByQrCode
from app.modules.restaurant.domain.entities import (
    RestaurantMenuAvailabilityStatus,
    RestaurantTableStatus,
)
from app.modules.restaurant.domain.exceptions import RestaurantTableNotFoundError
from app.modules.restaurant.domain.repositories import (
    RestaurantPublicMenuRepository,
    RestaurantTableRepository,
)
from app.modules.restaurant.infrastructure.models import RestaurantMenuAvailabilityModel


@dataclass(frozen=True)
class PublicMenuItem:
    name: str
    description: str | None
    sale_price: Decimal
    image_url: str | None
    service_period: str
    is_available: bool


@dataclass(frozen=True)
class PublicRestaurantMenu:
    restaurant_name: str
    currency: str
    table_number: str
    table_name: str | None
    service_date: date
    items: list[PublicMenuItem]


class GetRestaurantPublicMenu:
    def __init__(
        self,
        tables: RestaurantTableRepository,
        menus: RestaurantPublicMenuRepository,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.tables = tables
        self.menus = menus
        self.clock = clock or (lambda: datetime.now(UTC))

    async def execute(self, qr_code: str) -> PublicRestaurantMenu:
        table = await GetRestaurantTableByQrCode(self.tables).execute(qr_code)
        if table.status == RestaurantTableStatus.BLOCKED:
            raise RestaurantTableNotFoundError("Restaurant table not found.")

        context = await self.menus.active_branch_context(
            tenant_id=table.tenant_id,
            branch_id=table.branch_id,
        )
        if context is None:
            raise RestaurantTableNotFoundError("Restaurant table not found.")

        timezone_name, currency, restaurant_name = context
        service_date = self.clock().astimezone(ZoneInfo(timezone_name)).date()
        published_items = await self.menus.list_published_items(
            tenant_id=table.tenant_id,
            branch_id=table.branch_id,
            service_date=service_date,
        )
        items = [
            self._public_item(availability, product)
            for availability, product in published_items
            if "qr" in availability.channels
            and availability.status == RestaurantMenuAvailabilityStatus.PUBLISHED
            and availability.is_active
            and product.status == ProductStatus.ACTIVE
            and product.is_active
            and product.is_available_for_sale
        ]
        return PublicRestaurantMenu(
            restaurant_name=restaurant_name,
            currency=currency,
            table_number=table.number,
            table_name=table.name,
            service_date=service_date,
            items=items,
        )

    @staticmethod
    def _public_item(
        availability: RestaurantMenuAvailabilityModel,
        product: ProductModel,
    ) -> PublicMenuItem:
        remaining = (
            None
            if availability.available_quantity is None
            else availability.available_quantity - availability.sold_quantity
        )
        return PublicMenuItem(
            name=product.name,
            description=product.description,
            sale_price=product.sale_price,
            image_url=product.main_image_url,
            service_period=availability.service_period,
            is_available=remaining is None or remaining > 0,
        )
