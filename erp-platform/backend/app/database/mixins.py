from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.types import UUIDType


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )


class TenantMixin:
    tenant_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), index=True, nullable=False)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        server_default=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def mark_as_deleted(self) -> None:
        self.deleted_at = datetime.now(UTC)

    def restore(self) -> None:
        self.deleted_at = None


class AuditMixin:
    created_by: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    updated_by: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    deleted_by: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)


class CoreEntityMixin(
    UUIDPrimaryKeyMixin, TenantMixin, TimestampMixin, SoftDeleteMixin, AuditMixin
):
    """Mixin composto para futuras entidades multi-tenant."""
