"""inventory count

Revision ID: 0019_inventory_count
Revises: 0018_putaway
Create Date: 2026-10-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0019_inventory_count"
down_revision: str | None = "0018_putaway"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE inventory_movement_type ADD VALUE IF NOT EXISTS 'count'")
    op.execute(
        "DO $$ BEGIN CREATE TYPE inventory_count_status AS ENUM "
        "('draft', 'in_progress', 'finished', 'cancelled'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    inventory_count_status = postgresql.ENUM(
        "draft",
        "in_progress",
        "finished",
        "cancelled",
        name="inventory_count_status",
        create_type=False,
    )
    op.create_table(
        "inventory_counts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            sa.Uuid(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "warehouse_id",
            sa.Uuid(),
            sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("location_id", sa.Uuid(), nullable=True),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("status", inventory_count_status, nullable=False, server_default="draft"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column("deleted_by", sa.Uuid(), nullable=True),
        sa.UniqueConstraint(
            "tenant_id", "branch_id", "code", name="uq_inventory_counts_tenant_branch_code"
        ),
    )
    op.create_index(
        "ix_inventory_counts_tenant_branch_status",
        "inventory_counts",
        ["tenant_id", "branch_id", "status"],
    )
    op.create_table(
        "inventory_count_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "tenant_id",
            sa.Uuid(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "count_id",
            sa.Uuid(),
            sa.ForeignKey("inventory_counts.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Uuid(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("expected_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("counted_quantity", sa.Numeric(14, 3), nullable=True),
        sa.Column(
            "adjustment_movement_id",
            sa.Uuid(),
            sa.ForeignKey("inventory_movements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "expected_quantity >= 0", name="ck_inventory_count_item_expected_non_negative"
        ),
        sa.CheckConstraint(
            "counted_quantity IS NULL OR counted_quantity >= 0",
            name="ck_inventory_count_item_counted_non_negative",
        ),
        sa.UniqueConstraint(
            "count_id", "product_id", name="uq_inventory_count_items_count_product"
        ),
    )


def downgrade() -> None:
    op.drop_table("inventory_count_items")
    op.drop_index("ix_inventory_counts_tenant_branch_status", table_name="inventory_counts")
    op.drop_table("inventory_counts")
    sa.Enum(name="inventory_count_status").drop(op.get_bind(), checkfirst=True)
