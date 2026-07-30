from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, TimestampMixin
from app.database.types import UUIDType


class TenantEntitlementModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "tenant_entitlements"
    __table_args__ = (
        UniqueConstraint("tenant_id", "entitlement_key", name="uq_tenant_entitlements_key"),
        Index("ix_tenant_entitlements_tenant_enabled", "tenant_id", "is_enabled"),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    subscription_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=True
    )
    entitlement_key: Mapped[str] = mapped_column(String(80), nullable=False)
    entitlement_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source: Mapped[str] = mapped_column(String(40), default="plan", nullable=False)
