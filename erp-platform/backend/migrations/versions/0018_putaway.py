"""put away

Revision ID: 0018_putaway
Revises: 0017_goods_receipt
Create Date: 2026-08-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018_putaway"
down_revision: str | None = "0017_goods_receipt"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE inventory_movement_type ADD VALUE IF NOT EXISTS 'putaway'")
    op.execute("ALTER TYPE receiving_document_status ADD VALUE IF NOT EXISTS 'available'")
    op.add_column(
        "inventory_movements",
        sa.Column("origin_module", sa.String(length=80), nullable=False, server_default="MANUAL"),
    )
    op.add_column(
        "inventory_movements",
        sa.Column(
            "business_process",
            sa.String(length=80),
            nullable=False,
            server_default="MANUAL",
        ),
    )
    op.create_index(
        "ix_inventory_movements_origin",
        "inventory_movements",
        ["origin_module", "business_process"],
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_movements_origin", table_name="inventory_movements")
    op.drop_column("inventory_movements", "business_process")
    op.drop_column("inventory_movements", "origin_module")
