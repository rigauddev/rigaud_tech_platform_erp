from dataclasses import dataclass
from datetime import date
from uuid import UUID

from app.modules.restaurant.application.sector_use_cases import _branch, _text
from app.modules.restaurant.domain.entities import RestaurantMenuAvailabilityStatus
from app.modules.restaurant.domain.exceptions import (
    RestaurantInvalidDataError,
    RestaurantMenuAvailabilityAlreadyExistsError,
    RestaurantMenuAvailabilityNotFoundError,
)
from app.modules.restaurant.domain.repositories import RestaurantMenuAvailabilityRepository
from app.modules.restaurant.infrastructure.models import RestaurantMenuAvailabilityModel


@dataclass(frozen=True)
class MenuAvailabilityInput:
    tenant_id: UUID
    branch_id: UUID | None
    product_id: UUID
    service_date: date
    service_period: str
    channels: list[str]
    available_quantity: int | None
    status: RestaurantMenuAvailabilityStatus
    is_active: bool
    actor_id: UUID | None = None


def _period(value: str) -> str:
    return _text(value, limit=40).lower()


def _channels(values: list[str]) -> list[str]:
    cleaned = sorted({_text(value, limit=30).lower() for value in values})
    if not cleaned:
        raise RestaurantInvalidDataError("At least one sales channel is required.")
    return cleaned


class CreateRestaurantMenuAvailability:
    def __init__(self, repository: RestaurantMenuAvailabilityRepository) -> None:
        self.repository = repository

    async def execute(self, data: MenuAvailabilityInput) -> RestaurantMenuAvailabilityModel:
        branch_id, period = _branch(data.branch_id), _period(data.service_period)
        if data.available_quantity is not None and data.available_quantity < 0:
            raise RestaurantInvalidDataError("Available quantity cannot be negative.")
        if not await self.repository.product_exists(data.product_id, tenant_id=data.tenant_id):
            raise RestaurantInvalidDataError("Product must belong to the active tenant.")
        if await self.repository.exists_in_scope(
            tenant_id=data.tenant_id,
            branch_id=branch_id,
            product_id=data.product_id,
            service_date=data.service_date,
            service_period=period,
        ):
            raise RestaurantMenuAvailabilityAlreadyExistsError(
                "Menu item already exists for this service."
            )
        return await self.repository.add(
            RestaurantMenuAvailabilityModel(
                tenant_id=data.tenant_id,
                branch_id=branch_id,
                product_id=data.product_id,
                service_date=data.service_date,
                service_period=period,
                channels=_channels(data.channels),
                available_quantity=data.available_quantity,
                status=data.status,
                is_active=data.is_active,
                created_by=data.actor_id,
                updated_by=data.actor_id,
            )
        )


class ListRestaurantMenuAvailabilities:
    def __init__(self, repository: RestaurantMenuAvailabilityRepository) -> None:
        self.repository = repository

    async def execute(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        service_date: date | None,
        service_period: str | None,
    ) -> list[RestaurantMenuAvailabilityModel]:
        return await self.repository.list(
            tenant_id=tenant_id,
            branch_id=_branch(branch_id),
            service_date=service_date,
            service_period=_period(service_period) if service_period else None,
        )


class GetRestaurantMenuAvailability:
    def __init__(self, repository: RestaurantMenuAvailabilityRepository) -> None:
        self.repository = repository

    async def execute(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantMenuAvailabilityModel:
        item = await self.repository.get_by_id(item_id, tenant_id=tenant_id)
        if item is None:
            raise RestaurantMenuAvailabilityNotFoundError("Menu availability not found.")
        return item


class UpdateRestaurantMenuAvailability(CreateRestaurantMenuAvailability):
    async def execute(
        self, item_id: UUID, data: MenuAvailabilityInput
    ) -> RestaurantMenuAvailabilityModel:
        item = await GetRestaurantMenuAvailability(self.repository).execute(
            item_id, tenant_id=data.tenant_id
        )
        branch_id, period = _branch(data.branch_id), _period(data.service_period)
        if item.branch_id != branch_id:
            raise RestaurantInvalidDataError("Menu item must remain in the active branch.")
        if data.available_quantity is not None and data.available_quantity < item.sold_quantity:
            raise RestaurantInvalidDataError(
                "Available quantity cannot be less than sold quantity."
            )
        if not await self.repository.product_exists(data.product_id, tenant_id=data.tenant_id):
            raise RestaurantInvalidDataError("Product must belong to the active tenant.")
        if await self.repository.exists_in_scope(
            tenant_id=data.tenant_id,
            branch_id=branch_id,
            product_id=data.product_id,
            service_date=data.service_date,
            service_period=period,
            exclude_id=item.id,
        ):
            raise RestaurantMenuAvailabilityAlreadyExistsError(
                "Menu item already exists for this service."
            )
        item.product_id, item.service_date, item.service_period = (
            data.product_id,
            data.service_date,
            period,
        )
        item.channels, item.available_quantity, item.status = (
            _channels(data.channels),
            data.available_quantity,
            data.status,
        )
        item.is_active, item.updated_by = data.is_active, data.actor_id
        return await self.repository.add(item)


class DeleteRestaurantMenuAvailability:
    def __init__(self, repository: RestaurantMenuAvailabilityRepository) -> None:
        self.repository = repository

    async def execute(
        self, item_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantMenuAvailabilityModel:
        item = await GetRestaurantMenuAvailability(self.repository).execute(
            item_id, tenant_id=tenant_id
        )
        item.is_active, item.deleted_by, item.updated_by = False, actor_id, actor_id
        item.mark_as_deleted()
        return await self.repository.add(item)
