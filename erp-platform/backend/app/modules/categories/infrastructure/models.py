from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.categories.domain.entities import CategoryStatus


class CategoryModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "slug", name="uq_categories_tenant_id_slug"),
        UniqueConstraint(
            "tenant_id",
            "internal_code",
            name="uq_categories_tenant_id_internal_code",
        ),
        Index("ix_categories_tenant_parent", "tenant_id", "parent_id"),
        Index("ix_categories_tenant_status", "tenant_id", "status"),
        Index("ix_categories_tenant_order", "tenant_id", "display_order", "name"),
        CheckConstraint("display_order >= 0", name="ck_categories_display_order_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    parent_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=True,
    )
    internal_code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(80), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    icon: Mapped[str | None] = mapped_column(String(80), nullable=True)
    color: Mapped[str | None] = mapped_column(String(7), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[CategoryStatus] = mapped_column(
        Enum(
            CategoryStatus,
            name="category_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=CategoryStatus.ACTIVE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = CategoryStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = CategoryStatus.INACTIVE
        self.is_active = False
