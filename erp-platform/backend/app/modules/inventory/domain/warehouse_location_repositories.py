from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.inventory.infrastructure.models import WarehouseLocationModel


class WarehouseLocationRepository(ABC):
    @abstractmethod
    async def add(self, location: WarehouseLocationModel) -> WarehouseLocationModel:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(
        self, location_id: UUID, *, tenant_id: UUID
    ) -> WarehouseLocationModel | None:
        raise NotImplementedError

    @abstractmethod
    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
        is_active: bool | None,
        limit: int,
        offset: int,
    ) -> list[WarehouseLocationModel]:
        raise NotImplementedError

    @abstractmethod
    async def count(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        warehouse_id: UUID | None,
        zone_id: UUID | None,
        search: str | None,
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

    @abstractmethod
    async def exists_by_barcode(
        self,
        barcode: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def exists_by_qr_code(
        self,
        qr_code: str,
        *,
        tenant_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool:
        raise NotImplementedError
