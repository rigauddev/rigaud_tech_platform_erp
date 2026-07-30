from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.auth.domain.mfa import MfaMethodStatus, MfaMethodType
from app.modules.users.domain.entities import UserStatus


class AuthUserModel(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "auth_users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_auth_users_tenant_id_email"),
        UniqueConstraint("tenant_slug", "email", name="uq_auth_users_tenant_slug_email"),
    )

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    tenant_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), index=True, nullable=False)
    tenant_slug: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    display_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    status: Mapped[UserStatus] = mapped_column(
        Enum(
            UserStatus,
            name="user_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=UserStatus.ACTIVE,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    must_change_password: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def activate(self) -> None:
        self.status = UserStatus.ACTIVE
        self.is_active = True
        self.locked_until = None

    def deactivate(self) -> None:
        self.status = UserStatus.INACTIVE
        self.is_active = False

    def block(self) -> None:
        self.status = UserStatus.BLOCKED
        self.is_active = False

    def unblock(self) -> None:
        self.activate()


class AuthSessionModel(TimestampMixin, Base):
    __tablename__ = "auth_sessions"

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), index=True, nullable=False)
    membership_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), index=True, nullable=True
    )
    branch_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), index=True, nullable=True
    )
    branch_membership_id: Mapped[UUID | None] = mapped_column(UUIDType(as_uuid=True), nullable=True)
    role: Mapped[str | None] = mapped_column(String(64), nullable=True)
    access_scope: Mapped[str | None] = mapped_column(String(64), nullable=True)
    refresh_token_hash: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    replaced_by_session_id: Mapped[UUID | None] = mapped_column(
        UUIDType(as_uuid=True), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)


class UserMfaMethodModel(TimestampMixin, Base):
    __tablename__ = "user_mfa_methods"
    __table_args__ = (
        UniqueConstraint("user_id", "method_type", name="uq_user_mfa_methods_user_id_method_type"),
        Index("ix_user_mfa_methods_user_status", "user_id", "status"),
        Index("ix_user_mfa_methods_tenant_type", "tenant_id", "method_type"),
        Index(
            "ix_user_mfa_methods_primary",
            "user_id",
            "is_primary",
            unique=True,
            postgresql_where=text("is_primary = true"),
        ),
    )

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), index=True, nullable=False)
    method_type: Mapped[MfaMethodType] = mapped_column(
        Enum(
            MfaMethodType,
            name="mfa_method_type",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        index=True,
        nullable=False,
    )
    status: Mapped[MfaMethodStatus] = mapped_column(
        Enum(
            MfaMethodStatus,
            name="mfa_method_status",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        default=MfaMethodStatus.PENDING,
        index=True,
        nullable=False,
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    encrypted_secret: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    destination_masked: Mapped[str | None] = mapped_column(String(120), nullable=True)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MfaRecoveryCodeModel(TimestampMixin, Base):
    __tablename__ = "mfa_recovery_codes"
    __table_args__ = (
        UniqueConstraint("code_hash", name="uq_mfa_recovery_codes_code_hash"),
        Index("ix_mfa_recovery_codes_user_used", "user_id", "used_at"),
    )

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tenant_id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), index=True, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
