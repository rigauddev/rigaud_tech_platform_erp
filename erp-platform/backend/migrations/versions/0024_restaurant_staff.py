"""restaurant staff

Revision ID: 0024_restaurant_staff
Revises: 0023_restaurant_sectors
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0024_restaurant_staff"
down_revision: str | None = "0023_restaurant_sectors"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE restaurant_staff_role AS ENUM ('waiter', 'attendant', 'manager'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    op.execute(
        "DO $$ BEGIN CREATE TYPE restaurant_staff_status AS ENUM ('available', 'serving', 'paused', 'offline'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    staff_role = postgresql.ENUM(
        "waiter", "attendant", "manager", name="restaurant_staff_role", create_type=False
    )
    staff_status = postgresql.ENUM(
        "available",
        "serving",
        "paused",
        "offline",
        name="restaurant_staff_status",
        create_type=False,
    )
    op.create_table(
        "restaurant_staff",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id", sa.UUID(), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column(
            "user_id", sa.UUID(), sa.ForeignKey("auth_users.id", ondelete="SET NULL"), nullable=True
        ),
        sa.Column(
            "sector_id",
            sa.UUID(),
            sa.ForeignKey("restaurant_sectors.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(160), nullable=False),
        sa.Column("role", staff_role, nullable=False, server_default="waiter"),
        sa.Column("status", staff_status, nullable=False, server_default="available"),
        sa.Column(
            "can_receive_online_orders", sa.Boolean(), nullable=False, server_default=sa.true()
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
    )
    op.create_index(
        "uq_restaurant_staff_tenant_branch_code",
        "restaurant_staff",
        ["tenant_id", "branch_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_restaurant_staff_tenant_branch", "restaurant_staff", ["tenant_id", "branch_id"]
    )


def downgrade() -> None:
    op.drop_table("restaurant_staff")
    sa.Enum(name="restaurant_staff_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="restaurant_staff_role").drop(op.get_bind(), checkfirst=True)
