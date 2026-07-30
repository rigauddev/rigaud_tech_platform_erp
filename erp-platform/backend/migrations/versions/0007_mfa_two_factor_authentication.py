"""add mfa two factor authentication

Revision ID: 0007_mfa_2fa
Revises: 0006_audit_governance
Create Date: 2026-07-30 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0007_mfa_2fa"
down_revision: str | None = "0006_audit_governance"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    method_type = postgresql.ENUM(
        "totp", "email", "sms", "recovery_code", name="mfa_method_type", create_type=False
    )
    method_status = postgresql.ENUM(
        "pending", "active", "disabled", name="mfa_method_status", create_type=False
    )
    method_type.create(op.get_bind(), checkfirst=True)
    method_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "user_mfa_methods",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("method_type", method_type, nullable=False),
        sa.Column("status", method_status, nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("encrypted_secret", sa.String(length=1024), nullable=True),
        sa.Column("destination_masked", sa.String(length=120), nullable=True),
        sa.Column("verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "method_type", name="uq_user_mfa_methods_user_id_method_type"
        ),
    )
    op.create_index(op.f("ix_user_mfa_methods_user_id"), "user_mfa_methods", ["user_id"])
    op.create_index(op.f("ix_user_mfa_methods_tenant_id"), "user_mfa_methods", ["tenant_id"])
    op.create_index(op.f("ix_user_mfa_methods_method_type"), "user_mfa_methods", ["method_type"])
    op.create_index(op.f("ix_user_mfa_methods_status"), "user_mfa_methods", ["status"])
    op.create_index(
        "ix_user_mfa_methods_user_status",
        "user_mfa_methods",
        ["user_id", "status"],
    )
    op.create_index(
        "ix_user_mfa_methods_tenant_type",
        "user_mfa_methods",
        ["tenant_id", "method_type"],
    )
    op.create_index(
        "ix_user_mfa_methods_primary",
        "user_mfa_methods",
        ["user_id", "is_primary"],
        unique=True,
        postgresql_where=sa.text("is_primary = true"),
    )

    op.create_table(
        "mfa_recovery_codes",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("code_hash", sa.String(length=128), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code_hash", name="uq_mfa_recovery_codes_code_hash"),
    )
    op.create_index(op.f("ix_mfa_recovery_codes_user_id"), "mfa_recovery_codes", ["user_id"])
    op.create_index(op.f("ix_mfa_recovery_codes_tenant_id"), "mfa_recovery_codes", ["tenant_id"])
    op.create_index(op.f("ix_mfa_recovery_codes_used_at"), "mfa_recovery_codes", ["used_at"])
    op.create_index(
        "ix_mfa_recovery_codes_user_used",
        "mfa_recovery_codes",
        ["user_id", "used_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_mfa_recovery_codes_user_used", table_name="mfa_recovery_codes")
    op.drop_index(op.f("ix_mfa_recovery_codes_used_at"), table_name="mfa_recovery_codes")
    op.drop_index(op.f("ix_mfa_recovery_codes_tenant_id"), table_name="mfa_recovery_codes")
    op.drop_index(op.f("ix_mfa_recovery_codes_user_id"), table_name="mfa_recovery_codes")
    op.drop_table("mfa_recovery_codes")

    op.drop_index("ix_user_mfa_methods_primary", table_name="user_mfa_methods")
    op.drop_index("ix_user_mfa_methods_tenant_type", table_name="user_mfa_methods")
    op.drop_index("ix_user_mfa_methods_user_status", table_name="user_mfa_methods")
    op.drop_index(op.f("ix_user_mfa_methods_status"), table_name="user_mfa_methods")
    op.drop_index(op.f("ix_user_mfa_methods_method_type"), table_name="user_mfa_methods")
    op.drop_index(op.f("ix_user_mfa_methods_tenant_id"), table_name="user_mfa_methods")
    op.drop_index(op.f("ix_user_mfa_methods_user_id"), table_name="user_mfa_methods")
    op.drop_table("user_mfa_methods")

    sa.Enum(name="mfa_method_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="mfa_method_type").drop(op.get_bind(), checkfirst=True)
