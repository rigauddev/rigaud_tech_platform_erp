"""restaurant sectors

Revision ID: 0023_restaurant_sectors
Revises: 0022_restaurant_tables
Create Date: 2026-10-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0023_restaurant_sectors"
down_revision: str | None = "0022_restaurant_tables"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DO $$ BEGIN CREATE TYPE restaurant_sector_type AS ENUM ('dining_room', 'outdoor', 'bar', 'vip', 'counter', 'other'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    sector_type = postgresql.ENUM("dining_room", "outdoor", "bar", "vip", "counter", "other", name="restaurant_sector_type", create_type=False)
    op.create_table(
        "restaurant_sectors",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.UUID(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", sa.UUID(), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("floor_id", sa.UUID(), sa.ForeignKey("restaurant_floors.id", ondelete="SET NULL"), nullable=True),
        sa.Column("code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sector_type, nullable=False, server_default="dining_room"),
        sa.Column("color", sa.String(20), nullable=True),
        sa.Column("icon", sa.String(80), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
    )
    op.create_index("uq_restaurant_sectors_tenant_branch_code", "restaurant_sectors", ["tenant_id", "branch_id", "code"], unique=True, postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_restaurant_sectors_tenant_branch", "restaurant_sectors", ["tenant_id", "branch_id"])


def downgrade() -> None:
    op.drop_table("restaurant_sectors")
    sa.Enum(name="restaurant_sector_type").drop(op.get_bind(), checkfirst=True)
