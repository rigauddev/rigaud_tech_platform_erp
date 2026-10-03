from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.modules.inventory.application.validators import normalize_quantity
from app.modules.inventory.domain.entities import (
    InventoryCountStatus,
    InventoryMovementStatus,
    InventoryMovementType,
)
from app.modules.inventory.domain.exceptions import (
    InventoryBranchRequiredError,
    InventoryInvalidQuantityError,
    InventoryProductNotFoundError,
)
from app.modules.inventory.domain.repositories import InventoryRepository
from app.modules.inventory.infrastructure.count_repositories import (
    SQLAlchemyInventoryCountRepository,
)
from app.modules.inventory.infrastructure.models import (
    InventoryCountItemModel,
    InventoryCountModel,
    InventoryMovementModel,
)
from app.modules.products.domain.repositories import ProductRepository


class InventoryCountError(Exception):
    """Raised when a physical inventory count cannot change state."""


@dataclass(frozen=True)
class InventoryCountCreateInput:
    tenant_id: UUID
    branch_id: UUID | None
    warehouse_id: UUID
    code: str
    product_ids: list[UUID]
    location_id: UUID | None = None
    notes: str | None = None
    actor_id: UUID | None = None


class InventoryCountService:
    def __init__(
        self,
        counts: SQLAlchemyInventoryCountRepository,
        inventory: InventoryRepository,
        products: ProductRepository,
    ) -> None:
        self.counts = counts
        self.inventory = inventory
        self.products = products

    async def create(self, input_data: InventoryCountCreateInput) -> InventoryCountModel:
        branch_id = self._branch(input_data.branch_id)
        code = input_data.code.strip().upper()
        if not 2 <= len(code) <= 40 or not input_data.product_ids:
            raise InventoryCountError("A count code and at least one product are required.")
        if len(set(input_data.product_ids)) != len(input_data.product_ids):
            raise InventoryCountError("A product can only be counted once per document.")
        items: list[InventoryCountItemModel] = []
        for product_id in input_data.product_ids:
            if await self.products.get_by_id(product_id, tenant_id=input_data.tenant_id) is None:
                raise InventoryProductNotFoundError("Product not found.")
            balance = await self.inventory.get_balance(
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                product_id=product_id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
            )
            items.append(
                InventoryCountItemModel(
                    id=uuid4(),
                    tenant_id=input_data.tenant_id,
                    product_id=product_id,
                    expected_quantity=balance.physical_quantity if balance else Decimal("0.000"),
                )
            )
        return await self.counts.add(
            InventoryCountModel(
                id=uuid4(),
                tenant_id=input_data.tenant_id,
                branch_id=branch_id,
                warehouse_id=input_data.warehouse_id,
                location_id=input_data.location_id,
                code=code,
                status=InventoryCountStatus.DRAFT,
                notes=input_data.notes.strip() if input_data.notes else None,
                created_by=input_data.actor_id,
                updated_by=input_data.actor_id,
                items=items,
            )
        )

    async def start(
        self, count_id: UUID, *, tenant_id: UUID, branch_id: UUID | None, actor_id: UUID | None
    ) -> InventoryCountModel:
        count = await self._get(count_id, tenant_id, branch_id)
        if count.status != InventoryCountStatus.DRAFT:
            raise InventoryCountError("Only draft counts can be started.")
        count.status = InventoryCountStatus.IN_PROGRESS
        count.started_at = datetime.now(UTC)
        count.updated_by = actor_id
        return await self.counts.add(count)

    async def record_item(
        self,
        count_id: UUID,
        item_id: UUID,
        quantity: Decimal,
        *,
        tenant_id: UUID,
        branch_id: UUID | None,
        actor_id: UUID | None,
    ) -> InventoryCountModel:
        count = await self._get(count_id, tenant_id, branch_id)
        if count.status != InventoryCountStatus.IN_PROGRESS:
            raise InventoryCountError("Only counts in progress can receive quantities.")
        item = next((item for item in count.items if item.id == item_id), None)
        if item is None:
            raise InventoryCountError("Count item not found.")
        item.counted_quantity = normalize_quantity(quantity)
        count.updated_by = actor_id
        return await self.counts.add(count)

    async def finish(
        self, count_id: UUID, *, tenant_id: UUID, branch_id: UUID | None, actor_id: UUID | None
    ) -> InventoryCountModel:
        count = await self._get(count_id, tenant_id, branch_id)
        if count.status != InventoryCountStatus.IN_PROGRESS:
            raise InventoryCountError("Only counts in progress can be finished.")
        if any(item.counted_quantity is None for item in count.items):
            raise InventoryCountError("Every count item needs a counted quantity.")
        for item in count.items:
            balance = await self.inventory.get_or_create_balance(
                tenant_id=tenant_id,
                branch_id=count.branch_id,
                product_id=item.product_id,
                warehouse_id=count.warehouse_id,
                location_id=count.location_id,
            )
            delta = item.counted_quantity - balance.physical_quantity
            if delta == 0:
                continue
            if delta < 0 and balance.available_quantity + delta < 0:
                raise InventoryInvalidQuantityError(
                    "Count cannot reduce reserved or pending stock."
                )
            balance.physical_quantity += delta
            balance.updated_by = actor_id
            movement = await self.inventory.add_movement(
                InventoryMovementModel(
                    tenant_id=tenant_id,
                    branch_id=count.branch_id,
                    product_id=item.product_id,
                    warehouse_id=count.warehouse_id,
                    location_id=count.location_id,
                    movement_type=InventoryMovementType.COUNT,
                    status=InventoryMovementStatus.CONFIRMED,
                    physical_quantity_delta=delta,
                    reserved_quantity_delta=Decimal("0.000"),
                    putaway_pending_quantity_delta=Decimal("0.000"),
                    reason=f"Inventory count {count.code}",
                    source_module="inventory_count",
                    source_id=count.id,
                    origin_module="INVENTORY",
                    business_process="COUNT",
                    event_name="inventory.count.finished",
                    actor_id=actor_id,
                )
            )
            item.adjustment_movement_id = movement.id
            await self.inventory.add_balance(balance)
        count.status = InventoryCountStatus.FINISHED
        count.finished_at = datetime.now(UTC)
        count.updated_by = actor_id
        return await self.counts.add(count)

    async def cancel(
        self, count_id: UUID, *, tenant_id: UUID, branch_id: UUID | None, actor_id: UUID | None
    ) -> InventoryCountModel:
        count = await self._get(count_id, tenant_id, branch_id)
        if count.status == InventoryCountStatus.FINISHED:
            raise InventoryCountError("A finished count cannot be cancelled.")
        count.status = InventoryCountStatus.CANCELLED
        count.updated_by = actor_id
        return await self.counts.add(count)

    async def _get(
        self, count_id: UUID, tenant_id: UUID, branch_id: UUID | None
    ) -> InventoryCountModel:
        count = await self.counts.get_by_id(count_id, tenant_id=tenant_id)
        if count is None or (branch_id is not None and count.branch_id != branch_id):
            raise InventoryCountError("Inventory count not found.")
        return count

    @staticmethod
    def _branch(branch_id: UUID | None) -> UUID:
        if branch_id is None:
            raise InventoryBranchRequiredError("Active branch is required.")
        return branch_id
