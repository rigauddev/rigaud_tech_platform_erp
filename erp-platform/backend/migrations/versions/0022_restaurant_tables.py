"""restaurant tables and floor plans

Revision ID: 0022_restaurant_tables
Revises: 0021_inventory_transfers
Create Date: 2026-10-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_restaurant_tables"
down_revision: str | None = "0021_inventory_transfers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DO $$ BEGIN CREATE TYPE restaurant_table_shape AS ENUM ('square', 'round', 'rectangle'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    op.execute("DO $$ BEGIN CREATE TYPE restaurant_table_status AS ENUM ('available', 'occupied', 'reserved', 'order_pending', 'kitchen', 'waiting_payment', 'cleaning', 'blocked'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;")
    shape = postgresql.ENUM("square", "round", "rectangle", name="restaurant_table_shape", create_type=False)
    status = postgresql.ENUM("available", "occupied", "reserved", "order_pending", "kitchen", "waiting_payment", "cleaning", "blocked", name="restaurant_table_status", create_type=False)
    op.create_table(
        "restaurant_floors",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.UUID(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", sa.UUID(), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(40), nullable=False), sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True), sa.Column("deleted_by", sa.UUID(), nullable=True),
    )
    op.create_index("uq_restaurant_floors_tenant_branch_code", "restaurant_floors", ["tenant_id", "branch_id", "code"], unique=True, postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("ix_restaurant_floors_tenant_branch", "restaurant_floors", ["tenant_id", "branch_id"])
    op.create_table(
        "restaurant_tables",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column("tenant_id", sa.UUID(), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", sa.UUID(), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("floor_id", sa.UUID(), sa.ForeignKey("restaurant_floors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("number", sa.String(40), nullable=False), sa.Column("name", sa.String(120), nullable=True), sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("position_x", sa.Numeric(8, 2), nullable=False, server_default="0"), sa.Column("position_y", sa.Numeric(8, 2), nullable=False, server_default="0"),
        sa.Column("width", sa.Numeric(8, 2), nullable=False, server_default="96"), sa.Column("height", sa.Numeric(8, 2), nullable=False, server_default="72"),
        sa.Column("shape", shape, nullable=False, server_default="square"), sa.Column("status", status, nullable=False, server_default="available"),
        sa.Column("qr_code", sa.String(160), nullable=True), sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_by", sa.UUID(), nullable=True), sa.Column("updated_by", sa.UUID(), nullable=True), sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.CheckConstraint("capacity > 0", name="restaurant_table_capacity_positive"), sa.CheckConstraint("width > 0", name="restaurant_table_width_positive"), sa.CheckConstraint("height > 0", name="restaurant_table_height_positive"),
    )
    op.create_index("uq_restaurant_tables_tenant_floor_number", "restaurant_tables", ["tenant_id", "floor_id", "number"], unique=True, postgresql_where=sa.text("deleted_at IS NULL"))
    op.create_index("uq_restaurant_tables_tenant_qr_code", "restaurant_tables", ["tenant_id", "qr_code"], unique=True, postgresql_where=sa.text("qr_code IS NOT NULL AND deleted_at IS NULL"))
    op.create_index("ix_restaurant_tables_tenant_branch", "restaurant_tables", ["tenant_id", "branch_id"])
    op.create_index("ix_restaurant_tables_tenant_floor", "restaurant_tables", ["tenant_id", "floor_id"])
    op.create_index("ix_restaurant_tables_tenant_status", "restaurant_tables", ["tenant_id", "status"])


def downgrade() -> None:
    op.drop_table("restaurant_tables")
    op.drop_table("restaurant_floors")
    sa.Enum(name="restaurant_table_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="restaurant_table_shape").drop(op.get_bind(), checkfirst=True)
