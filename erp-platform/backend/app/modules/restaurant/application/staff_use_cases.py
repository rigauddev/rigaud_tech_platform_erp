from dataclasses import dataclass
from uuid import UUID

from app.modules.restaurant.application.sector_use_cases import _branch, _text
from app.modules.restaurant.domain.entities import RestaurantStaffRole, RestaurantStaffStatus
from app.modules.restaurant.domain.exceptions import (
    RestaurantInvalidDataError,
    RestaurantStaffCodeAlreadyExistsError,
    RestaurantStaffNotFoundError,
)
from app.modules.restaurant.domain.repositories import (
    RestaurantSectorRepository,
    RestaurantStaffRepository,
)
from app.modules.restaurant.infrastructure.models import RestaurantStaffModel


@dataclass(frozen=True)
class StaffInput:
    tenant_id: UUID
    branch_id: UUID | None
    code: str
    name: str
    role: RestaurantStaffRole
    status: RestaurantStaffStatus
    sector_id: UUID | None = None
    user_id: UUID | None = None
    can_receive_online_orders: bool = True
    is_active: bool = True
    actor_id: UUID | None = None


async def _validate_sector(
    sectors: RestaurantSectorRepository, data: StaffInput, branch_id: UUID
) -> None:
    if data.sector_id is None:
        return
    sector = await sectors.get_by_id(data.sector_id, tenant_id=data.tenant_id)
    if sector is None or sector.branch_id != branch_id:
        raise RestaurantInvalidDataError("Sector must belong to the active branch.")


class CreateRestaurantStaff:
    def __init__(
        self, staff: RestaurantStaffRepository, sectors: RestaurantSectorRepository
    ) -> None:
        self.staff = staff
        self.sectors = sectors

    async def execute(self, data: StaffInput) -> RestaurantStaffModel:
        branch_id = _branch(data.branch_id)
        code = _text(data.code, limit=40).upper()
        await _validate_sector(self.sectors, data, branch_id)
        if await self.staff.exists_by_code(code, tenant_id=data.tenant_id, branch_id=branch_id):
            raise RestaurantStaffCodeAlreadyExistsError("Restaurant staff code already exists.")
        return await self.staff.add(
            RestaurantStaffModel(
                tenant_id=data.tenant_id,
                branch_id=branch_id,
                user_id=data.user_id,
                sector_id=data.sector_id,
                code=code,
                name=_text(data.name, limit=160),
                role=data.role,
                status=data.status,
                can_receive_online_orders=data.can_receive_online_orders,
                is_active=data.is_active,
                created_by=data.actor_id,
                updated_by=data.actor_id,
            )
        )


class ListRestaurantStaff:
    def __init__(self, staff: RestaurantStaffRepository) -> None:
        self.staff = staff

    async def execute(
        self, *, tenant_id: UUID, branch_id: UUID | None, search: str | None = None
    ) -> list[RestaurantStaffModel]:
        return await self.staff.list(
            tenant_id=tenant_id, branch_id=_branch(branch_id), search=search
        )


class GetRestaurantStaff:
    def __init__(self, staff: RestaurantStaffRepository) -> None:
        self.staff = staff

    async def execute(self, staff_id: UUID, *, tenant_id: UUID) -> RestaurantStaffModel:
        item = await self.staff.get_by_id(staff_id, tenant_id=tenant_id)
        if item is None:
            raise RestaurantStaffNotFoundError("Restaurant staff not found.")
        return item


class UpdateRestaurantStaff:
    def __init__(
        self, staff: RestaurantStaffRepository, sectors: RestaurantSectorRepository
    ) -> None:
        self.staff = staff
        self.sectors = sectors

    async def execute(self, staff_id: UUID, data: StaffInput) -> RestaurantStaffModel:
        item = await GetRestaurantStaff(self.staff).execute(staff_id, tenant_id=data.tenant_id)
        branch_id = _branch(data.branch_id)
        code = _text(data.code, limit=40).upper()
        await _validate_sector(self.sectors, data, branch_id)
        if await self.staff.exists_by_code(
            code, tenant_id=data.tenant_id, branch_id=branch_id, exclude_id=item.id
        ):
            raise RestaurantStaffCodeAlreadyExistsError("Restaurant staff code already exists.")
        item.user_id, item.sector_id, item.code, item.name = (
            data.user_id,
            data.sector_id,
            code,
            _text(data.name, limit=160),
        )
        item.role, item.status = data.role, data.status
        item.can_receive_online_orders, item.is_active, item.updated_by = (
            data.can_receive_online_orders,
            data.is_active,
            data.actor_id,
        )
        return await self.staff.add(item)


class DeleteRestaurantStaff:
    def __init__(self, staff: RestaurantStaffRepository) -> None:
        self.staff = staff

    async def execute(
        self, staff_id: UUID, *, tenant_id: UUID, actor_id: UUID | None
    ) -> RestaurantStaffModel:
        item = await GetRestaurantStaff(self.staff).execute(staff_id, tenant_id=tenant_id)
        item.is_active = False
        item.mark_as_deleted()
        item.deleted_by, item.updated_by = actor_id, actor_id
        return await self.staff.add(item)
