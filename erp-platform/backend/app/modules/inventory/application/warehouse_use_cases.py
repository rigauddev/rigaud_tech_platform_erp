from dataclasses import dataclass
from uuid import UUID

from app.modules.inventory.application.validators import (
    normalize_optional_warehouse_text,
    normalize_warehouse_code,
    normalize_warehouse_text,
)
from app.modules.inventory.domain.exceptions import (
    WarehouseBranchRequiredError,
    WarehouseCodeAlreadyExistsError,
    WarehouseNotFoundError,
)
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import WarehouseModel


@dataclass(frozen=True)
class WarehouseCreateInput:
    tenant_id: UUID
    branch_id: UUID | None
    code: str
    name: str
    description: str | None = None
    address: str | None = None
    is_default: bool = False
    is_active: bool = True
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseUpdateInput:
    code: str | None = None
    name: str | None = None
    description: str | None = None
    address: str | None = None
    is_active: bool | None = None
    is_default: bool | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class WarehouseListInput:
    tenant_id: UUID
    branch_id: UUID | None = None
    is_active: bool | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class WarehouseListResult:
    items: list[WarehouseModel]
    total: int
    page: int
    page_size: int


class CreateWarehouse:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(self, input_data: WarehouseCreateInput) -> WarehouseModel:
        branch_id = _require_branch(input_data.branch_id)
        code = normalize_warehouse_code(input_data.code)
        if await self.warehouses.exists_by_code(
            code,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        ):
            raise WarehouseCodeAlreadyExistsError("Warehouse code already exists.")
        warehouse = WarehouseModel(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            code=code,
            name=normalize_warehouse_text(input_data.name, "name", max_length=120),
            description=normalize_optional_warehouse_text(
                input_data.description, "description", max_length=500
            ),
            address=normalize_optional_warehouse_text(
                input_data.address, "address", max_length=500
            ),
            is_default=input_data.is_default,
            is_active=input_data.is_active,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        if warehouse.is_active:
            warehouse.activate()
        else:
            warehouse.deactivate()
        if warehouse.is_default:
            await self.warehouses.unset_default_for_branch(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
            )
            warehouse.set_default()
        return await self.warehouses.add(warehouse)


class ListWarehouses:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(self, input_data: WarehouseListInput) -> WarehouseListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        items = await self.warehouses.list(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            is_active=input_data.is_active,
            limit=page_size,
            offset=offset,
        )
        total = await self.warehouses.count(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            is_active=input_data.is_active,
        )
        return WarehouseListResult(items=items, total=total, page=page, page_size=page_size)


class GetWarehouse:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(self, warehouse_id: UUID, *, tenant_id: UUID) -> WarehouseModel:
        warehouse = await self.warehouses.get_by_id(warehouse_id, tenant_id=tenant_id)
        if warehouse is None:
            raise WarehouseNotFoundError("Warehouse not found.")
        return warehouse


class UpdateWarehouse:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(
        self,
        warehouse_id: UUID,
        *,
        tenant_id: UUID,
        input_data: WarehouseUpdateInput,
    ) -> WarehouseModel:
        warehouse = await GetWarehouse(self.warehouses).execute(warehouse_id, tenant_id=tenant_id)
        if input_data.code is not None:
            code = normalize_warehouse_code(input_data.code)
            if await self.warehouses.exists_by_code(
                code,
                tenant_id=tenant_id,
                branch_id=warehouse.branch_id,
                exclude_id=warehouse.id,
            ):
                raise WarehouseCodeAlreadyExistsError("Warehouse code already exists.")
            warehouse.code = code
        if input_data.name is not None:
            warehouse.name = normalize_warehouse_text(input_data.name, "name", max_length=120)
        if input_data.description is not None:
            warehouse.description = normalize_optional_warehouse_text(
                input_data.description, "description", max_length=500
            )
        if input_data.address is not None:
            warehouse.address = normalize_optional_warehouse_text(
                input_data.address, "address", max_length=500
            )
        if input_data.is_active is not None:
            if input_data.is_active:
                warehouse.activate()
            else:
                warehouse.deactivate()
        if input_data.is_default:
            await self.warehouses.unset_default_for_branch(
                tenant_id=tenant_id,
                branch_id=warehouse.branch_id,
                except_id=warehouse.id,
            )
            warehouse.set_default()
        elif input_data.is_default is False:
            warehouse.is_default = False
        warehouse.updated_by = input_data.actor_id
        return await self.warehouses.add(warehouse)


class DeleteWarehouse:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(
        self,
        warehouse_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> WarehouseModel:
        warehouse = await GetWarehouse(self.warehouses).execute(warehouse_id, tenant_id=tenant_id)
        warehouse.deactivate()
        warehouse.mark_as_deleted()
        warehouse.deleted_by = actor_id
        warehouse.updated_by = actor_id
        return await self.warehouses.add(warehouse)


class SetDefaultWarehouse:
    def __init__(self, warehouses: WarehouseRepository) -> None:
        self.warehouses = warehouses

    async def execute(
        self,
        warehouse_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> WarehouseModel:
        warehouse = await GetWarehouse(self.warehouses).execute(warehouse_id, tenant_id=tenant_id)
        await self.warehouses.unset_default_for_branch(
            tenant_id=tenant_id,
            branch_id=warehouse.branch_id,
            except_id=warehouse.id,
        )
        warehouse.set_default()
        warehouse.updated_by = actor_id
        return await self.warehouses.add(warehouse)


def _require_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise WarehouseBranchRequiredError("Active branch is required.")
    return branch_id
