from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.inventory.domain.entities import (
    InventoryAdjustmentStatus,
    InventoryAdjustmentType,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryReservationStatus,
)


class InventoryBalanceModel(TenantMixin, TimestampMixin, AuditMixin, Base):
    __tablename__ = "inventory_balances"
    __table_args__ = (
        Index(
            "uq_inventory_balances_scope",
            "tenant_id",
            "branch_id",
            "product_id",
            "warehouse_id",
            "location_id",
            unique=True,
            postgresql_nulls_not_distinct=True,
        ),
        Index("ix_inventory_balances_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_inventory_balances_tenant_product", "tenant_id", "product_id"),
        CheckConstraint(
            "physical_quantity >= 0", name="ck_inventory_balance_physical_non_negative"
        ),
        CheckConstraint(
            "reserved_quantity >= 0", name="ck_inventory_balance_reserved_non_negative"
        ),
        CheckConstraint(
            "reserved_quantity <= physical_quantity",
            name="ck_inventory_balance_reserved_lte_physical",
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    warehouse_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    physical_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0.000")
    )
    reserved_quantity: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0.000")
    )

    @property
    def available_quantity(self) -> Decimal:
        return self.physical_quantity - self.reserved_quantity


class InventoryMovementModel(TenantMixin, TimestampMixin, Base):
    __tablename__ = "inventory_movements"
    __table_args__ = (
        Index("ix_inventory_movements_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_inventory_movements_tenant_product", "tenant_id", "product_id"),
        Index("ix_inventory_movements_tenant_type", "tenant_id", "movement_type"),
        Index("ix_inventory_movements_source", "source_module", "source_id"),
        CheckConstraint(
            "physical_quantity_delta <> 0 OR reserved_quantity_delta <> 0",
            name="ck_inventory_movement_has_delta",
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    warehouse_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    movement_type: Mapped[InventoryMovementType] = mapped_column(
        Enum(
            InventoryMovementType,
            name="inventory_movement_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[InventoryMovementStatus] = mapped_column(
        Enum(
            InventoryMovementStatus,
            name="inventory_movement_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=InventoryMovementStatus.CONFIRMED,
        nullable=False,
    )
    physical_quantity_delta: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0.000")
    )
    reserved_quantity_delta: Mapped[Decimal] = mapped_column(
        Numeric(14, 3), nullable=False, default=Decimal("0.000")
    )
    reason: Mapped[str] = mapped_column(String(240), nullable=False)
    source_module: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    event_name: Mapped[str] = mapped_column(String(120), nullable=False)
    actor_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)


class InventoryAdjustmentModel(TenantMixin, TimestampMixin, AuditMixin, Base):
    __tablename__ = "inventory_adjustments"
    __table_args__ = (
        Index("ix_inventory_adjustments_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_inventory_adjustments_tenant_product", "tenant_id", "product_id"),
        CheckConstraint("quantity > 0", name="ck_inventory_adjustment_quantity_positive"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    movement_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("inventory_movements.id", ondelete="RESTRICT"),
        nullable=True,
    )
    warehouse_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    adjustment_type: Mapped[InventoryAdjustmentType] = mapped_column(
        Enum(
            InventoryAdjustmentType,
            name="inventory_adjustment_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
    )
    status: Mapped[InventoryAdjustmentStatus] = mapped_column(
        Enum(
            InventoryAdjustmentStatus,
            name="inventory_adjustment_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=InventoryAdjustmentStatus.CONFIRMED,
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    reason: Mapped[str] = mapped_column(String(240), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class InventoryReservationModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        Index("ix_inventory_reservations_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_inventory_reservations_tenant_product", "tenant_id", "product_id"),
        Index("ix_inventory_reservations_tenant_status", "tenant_id", "status"),
        Index("ix_inventory_reservations_source", "source_module", "source_id"),
        CheckConstraint("quantity > 0", name="ck_inventory_reservation_quantity_positive"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    warehouse_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    location_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    status: Mapped[InventoryReservationStatus] = mapped_column(
        Enum(
            InventoryReservationStatus,
            name="inventory_reservation_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=InventoryReservationStatus.ACTIVE,
        nullable=False,
    )
    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    reason: Mapped[str] = mapped_column(String(240), nullable=False)
    source_module: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)

    def release(self) -> None:
        self.status = InventoryReservationStatus.RELEASED
        self.mark_as_deleted()
