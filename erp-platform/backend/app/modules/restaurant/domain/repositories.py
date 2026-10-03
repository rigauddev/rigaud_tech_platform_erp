from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.restaurant.infrastructure.models import RestaurantFloorModel, RestaurantTableModel


class RestaurantFloorRepository(ABC):
    @abstractmethod
    async def add(self, item: RestaurantFloorModel) -> RestaurantFloorModel: ...
    @abstractmethod
    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantFloorModel | None: ...
    @abstractmethod
    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, is_active: bool | None
    ) -> list[RestaurantFloorModel]: ...
    @abstractmethod
    async def exists_by_code(
        self, code: str, *, tenant_id: UUID, branch_id: UUID, exclude_id: UUID | None = None
    ) -> bool: ...


class RestaurantTableRepository(ABC):
    @abstractmethod
    async def add(self, item: RestaurantTableModel) -> RestaurantTableModel: ...
    @abstractmethod
    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantTableModel | None: ...
    @abstractmethod
    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, floor_id: UUID | None, is_active: bool | None
    ) -> list[RestaurantTableModel]: ...
    @abstractmethod
    async def exists_by_number(
        self, number: str, *, tenant_id: UUID, floor_id: UUID, exclude_id: UUID | None = None
    ) -> bool: ...
