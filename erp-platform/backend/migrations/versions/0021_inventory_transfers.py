"""inventory transfers

Revision ID: 0021_inventory_transfers
Revises: 0020_stock_adjustments
Create Date: 2026-10-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_inventory_transfers"
down_revision: str | None = "0020_stock_adjustments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE inventory_movement_type ADD VALUE IF NOT EXISTS 'transfer_out'")
    op.execute("ALTER TYPE inventory_movement_type ADD VALUE IF NOT EXISTS 'transfer_in'")
    op.execute(
        "DO $$ BEGIN CREATE TYPE inventory_transfer_status AS ENUM "
        "('draft', 'requested', 'in_transit', 'received', 'cancelled'); "
        "EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    status = postgresql.ENUM(
        "draft",
        "requested",
        "in_transit",
        "received",
        "cancelled",
        name="inventory_transfer_status",
        create_type=False,
    )
    op.create_table(
        "inventory_transfers",
        sa.Column("id", sa.UUID(), primary_key=True, nullable=False),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            sa.ForeignKey("companies.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column(
            "product_id",
            sa.UUID(),
            sa.ForeignKey("products.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "source_branch_id",
            sa.UUID(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "source_warehouse_id",
            sa.UUID(),
            sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("source_location_id", sa.UUID(), nullable=True),
        sa.Column(
            "target_branch_id",
            sa.UUID(),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "target_warehouse_id",
            sa.UUID(),
            sa.ForeignKey("warehouses.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("target_location_id", sa.UUID(), nullable=True),
        sa.Column("quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("status", status, nullable=False, server_default="requested"),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "outbound_movement_id",
            sa.UUID(),
            sa.ForeignKey("inventory_movements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column(
            "inbound_movement_id",
            sa.UUID(),
            sa.ForeignKey("inventory_movements.id", ondelete="RESTRICT"),
            nullable=True,
        ),
        sa.Column("dispatched_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_transfer_quantity_positive"),
        sa.CheckConstraint(
            "source_warehouse_id <> target_warehouse_id",
            name="ck_inventory_transfer_distinct_warehouses",
        ),
    )
    op.create_index(
        "uq_inventory_transfers_tenant_code",
        "inventory_transfers",
        ["tenant_id", "code"],
        unique=True,
    )
    op.create_index(
        "ix_inventory_transfers_tenant_source_status",
        "inventory_transfers",
        ["tenant_id", "source_branch_id", "status"],
    )
    op.create_index(
        "ix_inventory_transfers_tenant_target_status",
        "inventory_transfers",
        ["tenant_id", "target_branch_id", "status"],
    )


def downgrade() -> None:
    op.drop_table("inventory_transfers")
    sa.Enum(name="inventory_transfer_status").drop(op.get_bind(), checkfirst=True)
