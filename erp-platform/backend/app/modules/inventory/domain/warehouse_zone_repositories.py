from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.inventory.infrastructure.models import WarehouseZoneModel


class WarehouseZoneRepository(ABC):
    @abstractmethod
    async def add(self, zone: WarehouseZoneModel) -> WarehouseZoneModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, zone_id: UUID, *, tenant_id: UUID) -> WarehouseZoneModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseZoneModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        is_active: bool | None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        warehouse_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError
