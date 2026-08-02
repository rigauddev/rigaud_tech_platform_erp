from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
)


class InventoryRepository(ABC):
    @abstractmethod
    async def add_balance(self, balance: InventoryBalanceModel) -> InventoryBalanceModel:
        raise NotImplementedError

    @abstractmethod
    async def add_movement(self, movement: InventoryMovementModel) -> InventoryMovementModel:
        raise NotImplementedError

    @abstractmethod
    async def add_adjustment(
        self, adjustment: InventoryAdjustmentModel
    ) -> InventoryAdjustmentModel:
        raise NotImplementedError

    @abstractmethod
    async def add_reservation(
        self, reservation: InventoryReservationModel
    ) -> InventoryReservationModel:
        raise NotImplementedError

    @abstractmethod
    async def get_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel | None:
        raise NotImplementedError

    @abstractmethod
    async def get_or_create_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel:
        raise NotImplementedError

    @abstractmethod
    async def list_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryBalanceModel]:
        raise NotImplementedError

    @abstractmethod
    async def count_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def list_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryMovementModel]:
        raise NotImplementedError

    @abstractmethod
    async def count_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        raise NotImplementedError

    @abstractmethod
    async def get_reservation_by_id(
        self, reservation_id: UUID, *, tenant_id: UUID
    ) -> InventoryReservationModel | None:
        raise NotImplementedError
