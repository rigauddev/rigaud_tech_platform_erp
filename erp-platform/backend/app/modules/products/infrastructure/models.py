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
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TenantMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.products.domain.entities import ProductType, UnitOfMeasure


class ProductModel(TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("tenant_id", "internal_code", name="uq_products_tenant_id_internal_code"),
        Index(
            "uq_products_tenant_id_barcode_not_null",
            "tenant_id",
            "barcode",
            unique=True,
            postgresql_where=text("barcode IS NOT NULL"),
        ),
        Index("ix_products_tenant_active", "tenant_id", "is_active"),
        Index("ix_products_tenant_available", "tenant_id", "is_available_for_sale"),
        Index("ix_products_tenant_type", "tenant_id", "product_type"),
        CheckConstraint("sale_price >= 0", name="sale_price_non_negative"),
        CheckConstraint("cost_price >= 0", name="cost_price_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    internal_code: Mapped[str] = mapped_column(String(40), nullable=False)
    barcode: Mapped[str | None] = mapped_column(String(64), nullable=True)
    product_type: Mapped[ProductType] = mapped_column(
        Enum(
            ProductType,
            name="product_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=ProductType.SIMPLE,
        nullable=False,
    )
    unit_of_measure: Mapped[UnitOfMeasure] = mapped_column(
        Enum(
            UnitOfMeasure,
            name="product_unit_of_measure",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=UnitOfMeasure.UNIT,
        nullable=False,
    )
    sale_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    main_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_available_for_sale: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False
        self.is_available_for_sale = False

    def change_availability(self, available: bool) -> None:
        self.is_available_for_sale = available and self.is_active and not self.is_deleted
