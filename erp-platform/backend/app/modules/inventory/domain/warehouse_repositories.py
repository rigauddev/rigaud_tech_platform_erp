from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.inventory.infrastructure.models import WarehouseModel


class WarehouseRepository(ABC):
    @abstractmethod
    async def add(self, warehouse: WarehouseModel) -> WarehouseModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, warehouse_id: UUID, *, tenant_id: UUID) -> WarehouseModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def unset_default_for_branch(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        except_id: UUID | None = None,
    ) -> None:
        raise NotImplementedError
