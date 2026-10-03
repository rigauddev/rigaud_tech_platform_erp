from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.restaurant.infrastructure.models import (
    RestaurantFloorModel,
    RestaurantMenuAvailabilityModel,
    RestaurantSectorModel,
    RestaurantStaffModel,
    RestaurantTableModel,
)


class RestaurantMenuAvailabilityRepository(ABC):
    @abstractmethod
    async def add(
        self, item: RestaurantMenuAvailabilityModel
    ) -> RestaurantMenuAvailabilityModel: ...

    @abstractmethod
    async def get_by_id(
        self, item_id: UUID, *, tenant_id: UUID
    ) -> RestaurantMenuAvailabilityModel | None: ...

    @abstractmethod
    async def list(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        service_date: object | None,
        service_period: str | None,
    ) -> list[RestaurantMenuAvailabilityModel]: ...

    @abstractmethod
    async def exists_in_scope(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        service_date: object,
        service_period: str,
        exclude_id: UUID | None = None,
    ) -> bool: ...

    @abstractmethod
    async def product_exists(self, product_id: UUID, *, tenant_id: UUID) -> bool: ...


class RestaurantStaffRepository(ABC):
    @abstractmethod
    async def add(self, item: RestaurantStaffModel) -> RestaurantStaffModel: ...

    @abstractmethod
    async def get_by_id(self, item_id: UUID, *, tenant_id: UUID) -> RestaurantStaffModel | None: ...

    @abstractmethod
    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, search: str | None = None
    ) -> list[RestaurantStaffModel]: ...

    @abstractmethod
    async def exists_by_code(
        self, code: str, *, tenant_id: UUID, branch_id: UUID, exclude_id: UUID | None = None
    ) -> bool: ...


class RestaurantSectorRepository(ABC):
    @abstractmethod
    async def add(self, item: RestaurantSectorModel) -> RestaurantSectorModel: ...

    @abstractmethod
    async def get_by_id(
        self, item_id: UUID, *, tenant_id: UUID
    ) -> RestaurantSectorModel | None: ...

    @abstractmethod
    async def list(
        self, *, tenant_id: UUID, branch_id: UUID, is_active: bool | None
    ) -> list[RestaurantSectorModel]: ...

    @abstractmethod
    async def exists_by_code(
        self,
        code: str,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        exclude_id: UUID | None = None,
    ) -> bool: ...


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
