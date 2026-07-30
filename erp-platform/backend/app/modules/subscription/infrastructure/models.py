from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, TimestampMixin
from app.database.types import UUIDType


class SubscriptionModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint("tenant_id", name="uq_subscriptions_tenant_id"),
        Index("ix_subscriptions_status", "status"),
        CheckConstraint("grace_period_days >= 0", name="subscriptions_grace_period_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    plan_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("plans.id", ondelete="RESTRICT"), index=True
    )
    status: Mapped[str] = mapped_column(String(20), default="trial", nullable=False)
    billing_provider: Mapped[str] = mapped_column(String(40), default="fake", nullable=False)
    external_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    trial_ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    current_period_starts_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    current_period_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    grace_period_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    grace_period_days: Mapped[int] = mapped_column(default=7, nullable=False)
