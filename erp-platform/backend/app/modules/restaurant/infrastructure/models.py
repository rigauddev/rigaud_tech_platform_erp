from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.restaurant.domain.entities import (
    RestaurantMenuAvailabilityStatus,
    RestaurantSectorType,
    RestaurantStaffRole,
    RestaurantStaffStatus,
    RestaurantTableShape,
    RestaurantTableStatus,
)


class RestaurantMenuAvailabilityModel(
    TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base
):
    __tablename__ = "restaurant_menu_availabilities"
    __table_args__ = (
        Index(
            "uq_restaurant_menu_availability_scope",
            "tenant_id",
            "branch_id",
            "product_id",
            "service_date",
            "service_period",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index(
            "ix_restaurant_menu_availability_tenant_branch_date",
            "tenant_id",
            "branch_id",
            "service_date",
        ),
        CheckConstraint(
            "available_quantity IS NULL OR available_quantity >= 0",
            name="restaurant_menu_availability_quantity_nonnegative",
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    product_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    service_date: Mapped[date] = mapped_column(nullable=False, index=True)
    service_period: Mapped[str] = mapped_column(String(40), default="all_day", nullable=False)
    channels: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    available_quantity: Mapped[int | None] = mapped_column(nullable=True)
    sold_quantity: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[RestaurantMenuAvailabilityStatus] = mapped_column(
        Enum(
            RestaurantMenuAvailabilityStatus,
            name="restaurant_menu_availability_status",
            values_callable=lambda values: [item.value for item in values],
        ),
        default=RestaurantMenuAvailabilityStatus.PUBLISHED,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RestaurantStaffModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "restaurant_staff"
    __table_args__ = (
        Index(
            "uq_restaurant_staff_tenant_branch_code",
            "tenant_id",
            "branch_id",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_restaurant_staff_tenant_branch", "tenant_id", "branch_id"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    sector_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("restaurant_sectors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    role: Mapped[RestaurantStaffRole] = mapped_column(
        Enum(
            RestaurantStaffRole,
            name="restaurant_staff_role",
            values_callable=lambda values: [item.value for item in values],
        ),
        default=RestaurantStaffRole.WAITER,
        nullable=False,
    )
    status: Mapped[RestaurantStaffStatus] = mapped_column(
        Enum(
            RestaurantStaffStatus,
            name="restaurant_staff_status",
            values_callable=lambda values: [item.value for item in values],
        ),
        default=RestaurantStaffStatus.AVAILABLE,
        nullable=False,
    )
    can_receive_online_orders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RestaurantSectorModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "restaurant_sectors"
    __table_args__ = (
        Index(
            "uq_restaurant_sectors_tenant_branch_code",
            "tenant_id",
            "branch_id",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_restaurant_sectors_tenant_branch", "tenant_id", "branch_id"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    floor_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("restaurant_floors.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[RestaurantSectorType] = mapped_column(
        Enum(
            RestaurantSectorType,
            name="restaurant_sector_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=RestaurantSectorType.DINING_ROOM,
        nullable=False,
    )
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RestaurantFloorModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "restaurant_floors"
    __table_args__ = (
        Index(
            "uq_restaurant_floors_tenant_branch_code",
            "tenant_id",
            "branch_id",
            "code",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_restaurant_floors_tenant_branch", "tenant_id", "branch_id"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class RestaurantTableModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "restaurant_tables"
    __table_args__ = (
        Index(
            "uq_restaurant_tables_tenant_floor_number",
            "tenant_id",
            "floor_id",
            "number",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        Index("ix_restaurant_tables_tenant_branch", "tenant_id", "branch_id"),
        Index("ix_restaurant_tables_tenant_floor", "tenant_id", "floor_id"),
        Index("ix_restaurant_tables_tenant_status", "tenant_id", "status"),
        Index(
            "uq_restaurant_tables_tenant_qr_code",
            "tenant_id",
            "qr_code",
            unique=True,
            postgresql_where=text("qr_code IS NOT NULL AND deleted_at IS NULL"),
        ),
        CheckConstraint("capacity > 0", name="restaurant_table_capacity_positive"),
        CheckConstraint("width > 0", name="restaurant_table_width_positive"),
        CheckConstraint("height > 0", name="restaurant_table_height_positive"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("branches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    floor_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("restaurant_floors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    number: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    capacity: Mapped[int] = mapped_column(nullable=False)
    position_x: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal(0), nullable=False)
    position_y: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal(0), nullable=False)
    width: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal(96), nullable=False)
    height: Mapped[Decimal] = mapped_column(Numeric(8, 2), default=Decimal(72), nullable=False)
    shape: Mapped[RestaurantTableShape] = mapped_column(
        Enum(
            RestaurantTableShape,
            name="restaurant_table_shape",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=RestaurantTableShape.SQUARE,
        nullable=False,
    )
    status: Mapped[RestaurantTableStatus] = mapped_column(
        Enum(
            RestaurantTableStatus,
            name="restaurant_table_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=RestaurantTableStatus.AVAILABLE,
        nullable=False,
    )
    qr_code: Mapped[str | None] = mapped_column(String(160), nullable=True)
    sort_order: Mapped[int] = mapped_column(default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def deactivate(self) -> None:
        self.is_active = False
        self.status = RestaurantTableStatus.BLOCKED
