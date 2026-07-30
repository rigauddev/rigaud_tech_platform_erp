from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, TimestampMixin
from app.database.types import UUIDType


class FeatureFlagModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "feature_flags"
    __table_args__ = (
        UniqueConstraint("tenant_id", "feature_key", name="uq_feature_flags_tenant_feature"),
        Index("ix_feature_flags_scope_status", "scope", "status"),
        Index(
            "uq_feature_flags_global_feature",
            "feature_key",
            unique=True,
            postgresql_where=text("tenant_id IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    feature_key: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    scope: Mapped[str] = mapped_column(String(20), default="tenant", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="enabled", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
