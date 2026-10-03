from dataclasses import dataclass
from uuid import UUID

from app.modules.restaurant.domain.entities import RestaurantSectorType
from app.modules.restaurant.domain.exceptions import (
    RestaurantBranchRequiredError,
    RestaurantInvalidDataError,
    RestaurantSectorCodeAlreadyExistsError,
    RestaurantSectorNotFoundError,
)
from app.modules.restaurant.domain.repositories import (
    RestaurantFloorRepository,
    RestaurantSectorRepository,
)
from app.modules.restaurant.infrastructure.models import RestaurantSectorModel


@dataclass(frozen=True)
class SectorInput:
    tenant_id: UUID
    branch_id: UUID | None
    code: str
    name: str
    type: RestaurantSectorType
    floor_id: UUID | None = None
    description: str | None = None
    color: str | None = None
    icon: str | None = None
    sort_order: int = 0
    is_active: bool = True
    actor_id: UUID | None = None


def _branch(value: UUID | None) -> UUID:
    if value is None:
        raise RestaurantBranchRequiredError("Active branch is required.")
    return value


def _text(value: str, *, limit: int) -> str:
    normalized = value.strip()
    if not normalized or len(normalized) > limit:
        raise RestaurantInvalidDataError("Invalid restaurant sector data.")
    return normalized


async def _validate_floor(
    floors: RestaurantFloorRepository, data: SectorInput, branch_id: UUID
) -> None:
    if data.floor_id is None:
        return
    floor = await floors.get_by_id(data.floor_id, tenant_id=data.tenant_id)
    if floor is None or floor.branch_id != branch_id:
        raise RestaurantInvalidDataError("Floor must belong to the active branch.")


class CreateRestaurantSector:
    def __init__(
        self, sectors: RestaurantSectorRepository, floors: RestaurantFloorRepository
    ) -> None:
        self.sectors = sectors
        self.floors = floors

    async def execute(self, data: SectorInput) -> RestaurantSectorModel:
        branch_id = _branch(data.branch_id)
        code = _text(data.code, limit=40).upper()
        await _validate_floor(self.floors, data, branch_id)
        if await self.sectors.exists_by_code(code, tenant_id=data.tenant_id, branch_id=branch_id):
            raise RestaurantSectorCodeAlreadyExistsError("Restaurant sector code already exists.")
        return await self.sectors.add(
            RestaurantSectorModel(
                tenant_id=data.tenant_id,
                branch_id=branch_id,
                floor_id=data.floor_id,
                code=code,
                name=_text(data.name, limit=120),
                type=data.type,
                description=data.description.strip() if data.description else None,
                color=data.color.strip() if data.color else None,
                icon=data.icon.strip() if data.icon else None,
                sort_order=data.sort_order,
                is_active=data.is_active,
                created_by=data.actor_id,
                updated_by=data.actor_id,
            )
        )


class ListRestaurantSectors:
    def __init__(self, sectors: RestaurantSectorRepository) -> None:
        self.sectors = sectors

    async def execute(
        self, *, tenant_id: UUID, branch_id: UUID | None, is_active: bool | None
    ) -> list[RestaurantSectorModel]:
        return await self.sectors.list(
            tenant_id=tenant_id, branch_id=_branch(branch_id), is_active=is_active
        )


class GetRestaurantSector:
    def __init__(self, sectors: RestaurantSectorRepository) -> None:
        self.sectors = sectors

    async def execute(self, sector_id: UUID, *, tenant_id: UUID) -> RestaurantSectorModel:
        item = await self.sectors.get_by_id(sector_id, tenant_id=tenant_id)
        if item is None:
            raise RestaurantSectorNotFoundError("Restaurant sector not found.")
        return item


class UpdateRestaurantSector:
    def __init__(
        self, sectors: RestaurantSectorRepository, floors: RestaurantFloorRepository
    ) -> None:
        self.sectors = sectors
        self.floors = floors

    async def execute(self, sector_id: UUID, data: SectorInput) -> RestaurantSectorModel:
        item = await GetRestaurantSector(self.sectors).execute(sector_id, tenant_id=data.tenant_id)
        branch_id = _branch(data.branch_id)
        code = _text(data.code, limit=40).upper()
        await _validate_floor(self.floors, data, branch_id)
        if await self.sectors.exists_by_code(
            code,
            tenant_id=data.tenant_id,
            branch_id=branch_id,
            exclude_id=item.id,
        ):
            raise RestaurantSectorCodeAlreadyExistsError("Restaurant sector code already exists.")
        item.floor_id = data.floor_id
        item.code = code
        item.name = _text(data.name, limit=120)
        item.type = data.type
        item.description = data.description.strip() if data.description else None
        item.color = data.color.strip() if data.color else None
        item.icon = data.icon.strip() if data.icon else None
        item.sort_order = data.sort_order
        item.is_active = data.is_active
        item.updated_by = data.actor_id
        return await self.sectors.add(item)


class DeleteRestaurantSector:
    def __init__(self, sectors: RestaurantSectorRepository) -> None:
        self.sectors = sectors

    async def execute(
        self, sector_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantSectorModel:
        item = await GetRestaurantSector(self.sectors).execute(sector_id, tenant_id=tenant_id)
        item.is_active = False
        item.mark_as_deleted()
        item.deleted_by = actor_id
        item.updated_by = actor_id
        return await self.sectors.add(item)
