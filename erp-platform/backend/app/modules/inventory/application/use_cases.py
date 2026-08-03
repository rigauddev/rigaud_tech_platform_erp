from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.modules.inventory.application.validators import normalize_quantity, normalize_reason
from app.modules.inventory.domain.entities import (
    InventoryAdjustmentStatus,
    InventoryAdjustmentType,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryReservationStatus,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBalanceNotFoundError,
    InventoryBranchRequiredError,
    InventoryInsufficientStockError,
    InventoryProductNotFoundError,
    InventoryReservationInactiveError,
    InventoryReservationNotFoundError,
    InventoryWarehouseNotFoundError,
)
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.domain.warehouse_repositories import WarehouseRepository
from app.modules.inventory.infrastructure.models import (
    InventoryAdjustmentModel,
    InventoryBalanceModel,
    InventoryMovementModel,
    InventoryReservationModel,
)
from app.modules.products.domain.repositories import ProductRepository


@dataclass(frozen=True)
class InventoryListInput:
    tenant_id: UUID
    branch_id: UUID | None = None
    product_id: UUID | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class InventoryListResult:
    items: list[InventoryBalanceModel] | list[InventoryMovementModel]
    total: int
    page: int
    page_size: int


@dataclass(frozen=True)
class InventoryAdjustmentInput:
    tenant_id: UUID
    branch_id: UUID | None
    product_id: UUID
    adjustment_type: InventoryAdjustmentType
    quantity: Decimal | str | int
    reason: str
    warehouse_id: UUID | None = None
    location_id: UUID | None = None
    notes: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class InventoryReservationInput:
    tenant_id: UUID
    branch_id: UUID | None
    product_id: UUID
    quantity: Decimal | str | int
    reason: str
    warehouse_id: UUID | None = None
    location_id: UUID | None = None
    source_module: str | None = None
    source_id: UUID | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class InventoryOperationResult:
    balance: InventoryBalanceModel
    movement: InventoryMovementModel
    adjustment: InventoryAdjustmentModel | None = None
    reservation: InventoryReservationModel | None = None


class ListInventoryBalances:
    def __init__(self, inventory: InventoryRepository) -> None:
        self.inventory = inventory

    async def execute(self, input_data: InventoryListInput) -> InventoryListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        items = await self.inventory.list_balances(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            product_id=input_data.product_id,
            limit=page_size,
            offset=offset,
        )
        total = await self.inventory.count_balances(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            product_id=input_data.product_id,
        )
        return InventoryListResult(items=items, total=total, page=page, page_size=page_size)


class ListInventoryMovements:
    def __init__(self, inventory: InventoryRepository) -> None:
        self.inventory = inventory

    async def execute(self, input_data: InventoryListInput) -> InventoryListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        items = await self.inventory.list_movements(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            product_id=input_data.product_id,
            limit=page_size,
            offset=offset,
        )
        total = await self.inventory.count_movements(
            tenant_id=input_data.tenant_id,
            branch_id=input_data.branch_id,
            product_id=input_data.product_id,
        )
        return InventoryListResult(items=items, total=total, page=page, page_size=page_size)


class CreateInventoryAdjustment:
    def __init__(
        self,
        inventory: InventoryRepository,
        products: ProductRepository,
        warehouses: WarehouseRepository | None = None,
    ) -> None:
        self.inventory = inventory
        self.products = products
        self.warehouses = warehouses

    async def execute(self, input_data: InventoryAdjustmentInput) -> InventoryOperationResult:
        branch_id = _require_branch(input_data.branch_id)
        quantity = normalize_quantity(input_data.quantity)
        reason = normalize_reason(input_data.reason)
        await _ensure_product_exists(
            self.products,
            product_id=input_data.product_id,
            tenant_id=input_data.tenant_id,
        )
        await _ensure_warehouse_valid(
            self.warehouses,
            warehouse_id=input_data.warehouse_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        )
        balance = await self.inventory.get_or_create_balance(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            product_id=input_data.product_id,
            warehouse_id=input_data.warehouse_id,
            location_id=input_data.location_id,
        )
        physical_delta = quantity
        movement_type = InventoryMovementType.ADJUSTMENT_IN
        event_name = "inventory.adjusted.in"
        if input_data.adjustment_type == InventoryAdjustmentType.DECREASE:
            if balance.available_quantity < quantity:
                raise InventoryInsufficientStockError("Insufficient available stock.")
            physical_delta = -quantity
            movement_type = InventoryMovementType.ADJUSTMENT_OUT
            event_name = "inventory.adjusted.out"

        balance.physical_quantity += physical_delta
        balance.updated_by = input_data.actor_id
        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                product_id=input_data.product_id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
                movement_type=movement_type,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=physical_delta,
                reserved_quantity_delta=Decimal("0.000"),
                putaway_pending_quantity_delta=Decimal("0.000"),
                reason=reason,
                source_module="inventory",
                event_name=event_name,
                actor_id=input_data.actor_id,
            )
        )
        adjustment = await self.inventory.add_adjustment(
            InventoryAdjustmentModel(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                product_id=input_data.product_id,
                movement_id=movement.id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
                adjustment_type=input_data.adjustment_type,
                status=InventoryAdjustmentStatus.CONFIRMED,
                quantity=quantity,
                reason=reason,
                notes=input_data.notes,
                created_by=input_data.actor_id,
                updated_by=input_data.actor_id,
            )
        )
        await self.inventory.add_balance(balance)
        return InventoryOperationResult(balance=balance, movement=movement, adjustment=adjustment)


class CreateInventoryReservation:
    def __init__(
        self,
        inventory: InventoryRepository,
        products: ProductRepository,
        warehouses: WarehouseRepository | None = None,
    ) -> None:
        self.inventory = inventory
        self.products = products
        self.warehouses = warehouses

    async def execute(self, input_data: InventoryReservationInput) -> InventoryOperationResult:
        branch_id = _require_branch(input_data.branch_id)
        quantity = normalize_quantity(input_data.quantity)
        reason = normalize_reason(input_data.reason)
        await _ensure_product_exists(
            self.products,
            product_id=input_data.product_id,
            tenant_id=input_data.tenant_id,
        )
        await _ensure_warehouse_valid(
            self.warehouses,
            warehouse_id=input_data.warehouse_id,
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
        )
        balance = await self.inventory.get_or_create_balance(
            tenant_id=input_data.tenant_id,
            branch_id=branch_id,
            product_id=input_data.product_id,
            warehouse_id=input_data.warehouse_id,
            location_id=input_data.location_id,
        )
        if balance.available_quantity < quantity:
            raise InventoryInsufficientStockError("Insufficient available stock.")
        balance.reserved_quantity += quantity
        balance.updated_by = input_data.actor_id
        reservation = await self.inventory.add_reservation(
            InventoryReservationModel(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                product_id=input_data.product_id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
                status=InventoryReservationStatus.ACTIVE,
                quantity=quantity,
                reason=reason,
                source_module=input_data.source_module,
                source_id=input_data.source_id,
                created_by=input_data.actor_id,
                updated_by=input_data.actor_id,
            )
        )
        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                product_id=input_data.product_id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
                movement_type=InventoryMovementType.RESERVATION_CREATED,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=Decimal("0.000"),
                reserved_quantity_delta=quantity,
                putaway_pending_quantity_delta=Decimal("0.000"),
                reason=reason,
                source_module=input_data.source_module,
                source_id=input_data.source_id,
                event_name="inventory.reserved",
                actor_id=input_data.actor_id,
            )
        )
        await self.inventory.add_balance(balance)
        return InventoryOperationResult(
            balance=balance,
            movement=movement,
            reservation=reservation,
        )


class ReleaseInventoryReservation:
    def __init__(self, inventory: InventoryRepository) -> None:
        self.inventory = inventory

    async def execute(
        self,
        reservation_id: UUID,
        *,
        tenant_id: UUID,
        actor_id: UUID | None = None,
    ) -> InventoryOperationResult:
        reservation = await self.inventory.get_reservation_by_id(
            reservation_id, tenant_id=tenant_id
        )
        if reservation is None:
            raise InventoryReservationNotFoundError("Reservation not found.")
        if reservation.status != InventoryReservationStatus.ACTIVE:
            raise InventoryReservationInactiveError("Reservation is not active.")
        balance = await self.inventory.get_balance(
            tenant_id=tenant_id,
            branch_id=reservation.branch_id,
            product_id=reservation.product_id,
            warehouse_id=reservation.warehouse_id,
            location_id=reservation.location_id,
        )
        if balance is None:
            raise InventoryBalanceNotFoundError("Balance not found.")
        balance.reserved_quantity -= reservation.quantity
        balance.updated_by = actor_id
        reservation.release()
        reservation.deleted_by = actor_id
        reservation.updated_by = actor_id
        movement = await self.inventory.add_movement(
            InventoryMovementModel(
                tenant_id=tenant_id,
                branch_id=reservation.branch_id,
                product_id=reservation.product_id,
                warehouse_id=reservation.warehouse_id,
                location_id=reservation.location_id,
                movement_type=InventoryMovementType.RESERVATION_RELEASED,
                status=InventoryMovementStatus.CONFIRMED,
                physical_quantity_delta=Decimal("0.000"),
                reserved_quantity_delta=-reservation.quantity,
                putaway_pending_quantity_delta=Decimal("0.000"),
                reason=reservation.reason,
                source_module=reservation.source_module,
                source_id=reservation.source_id,
                event_name="inventory.reservation.released",
                actor_id=actor_id,
            )
        )
        await self.inventory.add_reservation(reservation)
        await self.inventory.add_balance(balance)
        return InventoryOperationResult(
            balance=balance,
            movement=movement,
            reservation=reservation,
        )


def _require_branch(branch_id: UUID | None) -> UUID:
    if branch_id is None:
        raise InventoryBranchRequiredError("Active branch is required.")
    return branch_id


async def _ensure_product_exists(
    products: ProductRepository,
    *,
    product_id: UUID,
    tenant_id: UUID,
) -> None:
    product = await products.get_by_id(product_id, tenant_id=tenant_id)
    if product is None:
        raise InventoryProductNotFoundError("Product not found.")


async def _ensure_warehouse_valid(
    warehouses: WarehouseRepository | None,
    *,
    warehouse_id: UUID | None,
    tenant_id: UUID,
    branch_id: UUID,
) -> None:
    if warehouse_id is None or warehouses is None:
        return
    warehouse = await warehouses.get_by_id(warehouse_id, tenant_id=tenant_id)
    if warehouse is None or warehouse.branch_id != branch_id or not warehouse.is_active:
        raise InventoryWarehouseNotFoundError("Warehouse not found.")
