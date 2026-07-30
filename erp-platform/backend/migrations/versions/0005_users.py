"""users module over auth_users

Revision ID: 0005_users
Revises: 0004_companies
Create Date: 2026-07-28 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

from app.database.types import UUIDType

revision: str = "0005_users"
down_revision: str | None = "0004_companies"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

USER_STATUS_ENUM = postgresql.ENUM(
    "active",
    "inactive",
    "blocked",
    name="user_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    USER_STATUS_ENUM.create(bind, checkfirst=True)

    op.add_column("auth_users", sa.Column("first_name", sa.String(length=80), nullable=True))
    op.add_column("auth_users", sa.Column("last_name", sa.String(length=120), nullable=True))
    op.add_column("auth_users", sa.Column("display_name", sa.String(length=160), nullable=True))
    op.add_column("auth_users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column(
        "auth_users",
        sa.Column("status", USER_STATUS_ENUM, server_default="active", nullable=False),
    )
    op.add_column(
        "auth_users",
        sa.Column("must_change_password", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "auth_users",
        sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "auth_users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column("auth_users", sa.Column("created_by", UUIDType(as_uuid=True), nullable=True))
    op.add_column("auth_users", sa.Column("updated_by", UUIDType(as_uuid=True), nullable=True))
    op.add_column("auth_users", sa.Column("deleted_by", UUIDType(as_uuid=True), nullable=True))

    op.create_index("ix_auth_users_status", "auth_users", ["status"])
    op.create_index("ix_auth_users_display_name", "auth_users", ["display_name"])
    op.create_index("ix_auth_users_last_login_at", "auth_users", ["last_login_at"])

    op.execute(
        """
        ALTER TABLE auth_users
        ADD CONSTRAINT fk_auth_users_tenant_id_companies
        FOREIGN KEY (tenant_id) REFERENCES companies(id) NOT VALID
        """
    )


def downgrade() -> None:
    op.drop_constraint("fk_auth_users_tenant_id_companies", "auth_users", type_="foreignkey")
    op.drop_index("ix_auth_users_last_login_at", table_name="auth_users")
    op.drop_index("ix_auth_users_display_name", table_name="auth_users")
    op.drop_index("ix_auth_users_status", table_name="auth_users")
    op.drop_column("auth_users", "deleted_by")
    op.drop_column("auth_users", "updated_by")
    op.drop_column("auth_users", "created_by")
    op.drop_column("auth_users", "locked_until")
    op.drop_column("auth_users", "failed_login_attempts")
    op.drop_column("auth_users", "must_change_password")
    op.drop_column("auth_users", "status")
    op.drop_column("auth_users", "phone")
    op.drop_column("auth_users", "display_name")
    op.drop_column("auth_users", "last_name")
    op.drop_column("auth_users", "first_name")
    USER_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
