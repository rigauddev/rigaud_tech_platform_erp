from uuid import UUID, uuid4

import pytest

from app.modules.inventory.application.warehouse_use_cases import (
    CreateWarehouse,
    SetDefaultWarehouse,
    WarehouseCreateInput,
)
from app.modules.inventory.domain.exceptions import WarehouseCodeAlreadyExistsError
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import WarehouseModel


@pytest.mark.asyncio
async def test_create_warehouse_normalizes_code_and_branch_scope() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    repository = _FakeWarehouseRepository()

    warehouse = await CreateWarehouse(repository).execute(
        WarehouseCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code=" main ",
            name="Depósito Principal",
            is_default=True,
            actor_id=uuid4(),
        )
    )

    assert warehouse.code == "MAIN"
    assert warehouse.tenant_id == tenant_id
    assert warehouse.branch_id == branch_id
    assert warehouse.is_default is True
    assert warehouse.is_active is True


@pytest.mark.asyncio
async def test_create_warehouse_rejects_duplicate_code_in_same_branch() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    repository = _FakeWarehouseRepository()
    await CreateWarehouse(repository).execute(
        WarehouseCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code="MAIN",
            name="Depósito Principal",
        )
    )

    with pytest.raises(WarehouseCodeAlreadyExistsError):
        await CreateWarehouse(repository).execute(
            WarehouseCreateInput(
                tenant_id=tenant_id,
                branch_id=branch_id,
                code="main",
                name="Outro depósito",
            )
        )


@pytest.mark.asyncio
async def test_set_default_warehouse_unsets_previous_default() -> None:
    tenant_id = uuid4()
    branch_id = uuid4()
    repository = _FakeWarehouseRepository()
    first = await CreateWarehouse(repository).execute(
        WarehouseCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code="MAIN",
            name="Depósito Principal",
            is_default=True,
        )
    )
    second = await CreateWarehouse(repository).execute(
        WarehouseCreateInput(
            tenant_id=tenant_id,
            branch_id=branch_id,
            code="BAR",
            name="Bar",
        )
    )

    updated = await SetDefaultWarehouse(repository).execute(second.id, tenant_id=tenant_id)

    assert updated.is_default is True
    assert repository.items[first.id].is_default is False


class _FakeWarehouseRepository(WarehouseRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, WarehouseModel] = {}

    async def add(self, warehouse: WarehouseModel) -> WarehouseModel:
        if warehouse.id is None:
            warehouse.id = uuid4()
        self.items[warehouse.id] = warehouse
        return warehouse

    async def get_by_id(self, warehouse_id: UUID, *, tenant_id: UUID) -> WarehouseModel | None:
        warehouse = self.items.get(warehouse_id)
        if warehouse and warehouse.tenant_id == tenant_id and warehouse.deleted_at is None:
            return warehouse
        return None

    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseModel]:
        items = [
            item
            for item in self.items.values()
            if item.tenant_id == tenant_id
            and item.deleted_at is None
            and (branch_id is None or item.branch_id == branch_id)
            and (is_active is None or item.is_active == is_active)
        ]
        return items[offset : offset + limit]

    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        return len(
            await self.list(
                tenant_id=tenant_id,
                branch_id=branch_id,
                is_active=is_active,
                limit=100,
                offset=0,
            )
        )

    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        return any(
            item.code == code
            and item.tenant_id == tenant_id
            and item.branch_id == branch_id
            and item.deleted_at is None
            and item.id != exclude_id
            for item in self.items.values()
        )

    async def unset_default_for_branch(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        except_id: UUID | None = None,
    ) -> None:
        for item in self.items.values():
            if item.tenant_id == tenant_id and item.branch_id == branch_id and item.id != except_id:
                item.is_default = False
