from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.inventory.domain.entities import (
    InventoryAdjustmentStatus,
    InventoryAdjustmentType,
    InventoryMovementStatus,
    InventoryMovementType,
    InventoryReservationStatus,
    ReceivingDocumentStatus,
    WarehouseLocationStatus,
    WarehouseStatus,
    WarehouseZoneStatus,
    WarehouseZoneType,
)


class WarehouseModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "warehouses"
    __table_args__ = (
        Index("uq_warehouses_tenant_branch_code", "tenant_id", "branch_id", "code", unique=True),
        Index(
            "uq_warehouses_tenant_branch_default",
            "tenant_id",
            "branch_id",
            unique=True,
            postgresql_where=text("is_default = true AND deleted_at IS NULL"),
        ),
        Index("ix_warehouses_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_warehouses_tenant_active", "tenant_id", "is_active"),
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
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[WarehouseStatus] = mapped_column(
        Enum(
            WarehouseStatus,
            name="warehouse_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=WarehouseStatus.ACTIVE,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = WarehouseStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = WarehouseStatus.INACTIVE
        self.is_active = False
        self.is_default = False

    def set_default(self) -> None:
        self.is_default = True
        self.activate()


class WarehouseZoneModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "warehouse_zones"
    __table_args__ = (
        Index(
            "uq_warehouse_zones_tenant_warehouse_code",
            "tenant_id",
            "warehouse_id",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_warehouse_zones_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_warehouse_zones_tenant_warehouse", "tenant_id", "warehouse_id"),
        Index("ix_warehouse_zones_tenant_active", "tenant_id", "is_active"),
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
    warehouse_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    type: Mapped[WarehouseZoneType] = mapped_column(
        Enum(
            WarehouseZoneType,
            name="warehouse_zone_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=WarehouseZoneType.STORAGE,
        nullable=False,
    )
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_receiving: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shipping: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_storage: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_quarantine: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[WarehouseZoneStatus] = mapped_column(
        Enum(
            WarehouseZoneStatus,
            name="warehouse_zone_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=WarehouseZoneStatus.ACTIVE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = WarehouseZoneStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = WarehouseZoneStatus.INACTIVE
        self.is_active = False


class WarehouseLocationModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "warehouse_locations"
    __table_args__ = (
        Index(
            "uq_warehouse_locations_tenant_warehouse_code",
            "tenant_id",
            "warehouse_id",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "uq_warehouse_locations_tenant_barcode",
            "tenant_id",
            "barcode",
            unique=True,
            postgresql_where=text("barcode IS NOT NULL AND deleted_at IS NULL"),
        ),
        Index(
            "uq_warehouse_locations_tenant_qr_code",
            "tenant_id",
            "qr_code",
            unique=True,
            postgresql_where=text("qr_code IS NOT NULL AND deleted_at IS NULL"),
        ),
        Index("ix_warehouse_locations_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_warehouse_locations_tenant_warehouse", "tenant_id", "warehouse_id"),
        Index("ix_warehouse_locations_tenant_zone", "tenant_id", "zone_id"),
        Index("ix_warehouse_locations_tenant_active", "tenant_id", "is_active"),
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
    warehouse_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    zone_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouse_zones.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(80), nullable=True)
    barcode: Mapped[str | None] = mapped_column(String(80), nullable=True)
    qr_code: Mapped[str | None] = mapped_column(String(160), nullable=True)
    aisle: Mapped[str | None] = mapped_column(String(40), nullable=True)
    rack: Mapped[str | None] = mapped_column(String(40), nullable=True)
    shelf: Mapped[str | None] = mapped_column(String(40), nullable=True)
    level: Mapped[str | None] = mapped_column(String(40), nullable=True)
    position: Mapped[str | None] = mapped_column(String(40), nullable=True)
    capacity: Mapped[Decimal | None] = mapped_column(Numeric(14, 3), nullable=True)
    capacity_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    allow_negative: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    allow_mixed_items: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    allow_expired: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_pick_location: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_receive_location: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_shipping_location: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[WarehouseLocationStatus] = mapped_column(
        Enum(
            WarehouseLocationStatus,
            name="warehouse_location_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=WarehouseLocationStatus.ACTIVE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = WarehouseLocationStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = WarehouseLocationStatus.INACTIVE
        self.is_active = False
        self.is_default = False


class ReceivingDocumentModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "receiving_documents"
    __table_args__ = (
        Index(
            "uq_receiving_documents_tenant_branch_number",
            "tenant_id",
            "branch_id",
            "document_number",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_receiving_documents_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_receiving_documents_tenant_warehouse", "tenant_id", "warehouse_id"),
        Index("ix_receiving_documents_tenant_status", "tenant_id", "status"),
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
    warehouse_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    supplier_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    document_number: Mapped[str] = mapped_column(String(60), nullable=False)
    document_type: Mapped[str] = mapped_column(String(40), nullable=False)
    status: Mapped[ReceivingDocumentStatus] = mapped_column(
        Enum(
            ReceivingDocumentStatus,
            name="receiving_document_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ReceivingDocumentStatus.DRAFT,
        nullable=False,
    )
    expected_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    received_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    items: Mapped[list["ReceivingItemModel"]] = relationship(
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ReceivingItemModel(TenantMixin, TimestampMixin, Base):
    __tablename__ = "receiving_items"
    __table_args__ = (
        Index("ix_receiving_items_tenant_document", "tenant_id", "document_id"),
        Index("ix_receiving_items_tenant_product", "tenant_id", "product_id"),
        CheckConstraint(
            "ordered_quantity >= 0",
            name="ck_receiving_item_ordered_non_negative",
        ),
        CheckConstraint(
            "received_quantity >= 0",
            name="ck_receiving_item_received_non_negative",
        ),
        CheckConstraint(
            "damaged_quantity >= 0",
            name="ck_receiving_item_damaged_non_negative",
        ),
        CheckConstraint(
            "pending_quantity >= 0",
            name="ck_receiving_item_pending_non_negative",
        ),
        CheckConstraint("unit_cost >= 0", name="ck_receiving_item_unit_cost_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    document_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("receiving_documents.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    ordered_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    received_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    damaged_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    pending_quantity: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    document: Mapped[ReceivingDocumentModel] = relationship(back_populates="items")


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
    warehouse_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
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
    warehouse_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
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
    warehouse_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
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
    warehouse_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("warehouses.id", ondelete="RESTRICT"),
        nullable=True,
    )
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
