from decimal import Decimal
from uuid import UUID

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
)


class SQLAlchemyInventoryRepository(InventoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_balance(self, balance: InventoryBalanceModel) -> InventoryBalanceModel:
        self.session.add(balance)
        await self.session.flush()
        return balance

    async def add_movement(self, movement: InventoryMovementModel) -> InventoryMovementModel:
        self.session.add(movement)
        await self.session.flush()
        return movement

    async def add_adjustment(
        self, adjustment: InventoryAdjustmentModel
    ) -> InventoryAdjustmentModel:
        self.session.add(adjustment)
        await self.session.flush()
        return adjustment

    async def add_reservation(
        self, reservation: InventoryReservationModel
    ) -> InventoryReservationModel:
        self.session.add(reservation)
        await self.session.flush()
        return reservation

    async def get_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel | None:
        statement = select(InventoryBalanceModel).where(
            InventoryBalanceModel.tenant_id == tenant_id,
            InventoryBalanceModel.branch_id == branch_id,
            InventoryBalanceModel.product_id == product_id,
        )
        statement = self._optional_scope(
            statement, warehouse_id=warehouse_id, location_id=location_id
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_or_create_balance(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID,
        product_id: UUID,
        warehouse_id: UUID | None = None,
        location_id: UUID | None = None,
    ) -> InventoryBalanceModel:
        balance = await self.get_balance(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
        )
        if balance is not None:
            return balance
        balance = InventoryBalanceModel(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
            warehouse_id=warehouse_id,
            location_id=location_id,
            physical_quantity=Decimal("0.000"),
            reserved_quantity=Decimal("0.000"),
            putaway_pending_quantity=Decimal("0.000"),
        )
        return await self.add_balance(balance)

    async def list_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryBalanceModel]:
        statement = self._balances_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
        )
        statement = (
            statement.order_by(InventoryBalanceModel.updated_at.desc()).limit(limit).offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_balances(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        statement = self._balances_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def list_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
        limit: int,
        offset: int,
    ) -> list[InventoryMovementModel]:
        statement = self._movements_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
        )
        statement = (
            statement.order_by(InventoryMovementModel.created_at.desc()).limit(limit).offset(offset)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_movements(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> int:
        statement = self._movements_select(
            tenant_id=tenant_id,
            branch_id=branch_id,
            product_id=product_id,
        )
        result = await self.session.execute(select(func.count()).select_from(statement.subquery()))
        return int(result.scalar_one())

    async def get_reservation_by_id(
        self, reservation_id: UUID, *, tenant_id: UUID
    ) -> InventoryReservationModel | None:
        result = await self.session.execute(
            select(InventoryReservationModel).where(
                InventoryReservationModel.id == reservation_id,
                InventoryReservationModel.tenant_id == tenant_id,
                InventoryReservationModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    def _balances_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> Select[tuple[InventoryBalanceModel]]:
        statement = select(InventoryBalanceModel).where(
            InventoryBalanceModel.tenant_id == tenant_id
        )
        if branch_id is not None:
            statement = statement.where(InventoryBalanceModel.branch_id == branch_id)
        if product_id is not None:
            statement = statement.where(InventoryBalanceModel.product_id == product_id)
        return statement

    def _movements_select(
        self,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        product_id: UUID | None,
    ) -> Select[tuple[InventoryMovementModel]]:
        statement = select(InventoryMovementModel).where(
            InventoryMovementModel.tenant_id == tenant_id
        )
        if branch_id is not None:
            statement = statement.where(InventoryMovementModel.branch_id == branch_id)
        if product_id is not None:
            statement = statement.where(InventoryMovementModel.product_id == product_id)
        return statement

    def _optional_scope(
        self,
        statement: Select[tuple[InventoryBalanceModel]],
        *,
        warehouse_id: UUID | None,
        location_id: UUID | None,
    ) -> Select[tuple[InventoryBalanceModel]]:
        if warehouse_id is None:
            statement = statement.where(InventoryBalanceModel.warehouse_id.is_(None))
        else:
            statement = statement.where(InventoryBalanceModel.warehouse_id == warehouse_id)
        if location_id is None:
            statement = statement.where(InventoryBalanceModel.location_id.is_(None))
        else:
            statement = statement.where(InventoryBalanceModel.location_id == location_id)
        return statement
