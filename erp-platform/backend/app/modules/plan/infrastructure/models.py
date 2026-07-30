from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin
from app.database.types import UUIDType


class PlanModel(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "plans"
    __table_args__ = (
        UniqueConstraint("code", name="uq_plans_code"),
        Index("ix_plans_status_active", "status", "is_active"),
        CheckConstraint("monthly_price >= 0", name="plans_monthly_price_non_negative"),
        CheckConstraint("annual_price >= 0", name="plans_annual_price_non_negative"),
        CheckConstraint("display_order >= 0", name="plans_display_order_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    monthly_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    annual_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False, default=Decimal("0.00")
    )
    trial_days: Mapped[int] = mapped_column(default=0, nullable=False)
    is_trial_available: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    display_order: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)


class PlanEntitlementModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "plan_entitlements"
    __table_args__ = (
        UniqueConstraint("plan_id", "entitlement_key", name="uq_plan_entitlements_plan_key"),
        Index("ix_plan_entitlements_key", "entitlement_key"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), index=True
    )
    entitlement_key: Mapped[str] = mapped_column(String(80), nullable=False)
    entitlement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class PlanLimitModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "plan_limits"
    __table_args__ = (
        UniqueConstraint("plan_id", "limit_key", name="uq_plan_limits_plan_key"),
        CheckConstraint("limit_value >= -1", name="plan_limits_value_valid"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    plan_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("plans.id", ondelete="CASCADE"), index=True
    )
    limit_key: Mapped[str] = mapped_column(String(80), nullable=False)
    limit_value: Mapped[int] = mapped_column(nullable=False)
    is_unlimited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
