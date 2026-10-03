from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
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
from app.modules.restaurant.domain.entities import RestaurantTableShape, RestaurantTableStatus


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
