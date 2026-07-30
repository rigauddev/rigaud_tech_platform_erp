from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, TimestampMixin
from app.database.types import UUIDType


class BillingEventModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "billing_events"
    __table_args__ = (
        Index("ix_billing_events_tenant_provider", "tenant_id", "provider"),
        Index("ix_billing_events_status", "status"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    subscription_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    provider: Mapped[str] = mapped_column(String(40), default="fake", nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="received", nullable=False)
    external_event_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
