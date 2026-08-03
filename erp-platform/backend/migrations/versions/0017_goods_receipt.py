"""goods receipt

Revision ID: 0017_goods_receipt
Revises: 0016_receiving_documents
Create Date: 2026-08-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017_goods_receipt"
down_revision: str | None = "0016_receiving_documents"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE inventory_movement_type ADD VALUE IF NOT EXISTS 'receipt'")
    op.execute("ALTER TYPE receiving_document_status ADD VALUE IF NOT EXISTS 'putaway_pending'")
    op.add_column(
        "inventory_balances",
        sa.Column(
            "putaway_pending_quantity",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0.000",
        ),
    )
    op.add_column(
        "inventory_movements",
        sa.Column(
            "putaway_pending_quantity_delta",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
            server_default="0.000",
        ),
    )
    op.drop_constraint(
        "ck_inventory_movement_has_delta",
        "inventory_movements",
        type_="check",
    )
    op.create_check_constraint(
        "ck_inventory_movement_has_delta",
        "inventory_movements",
        (
            "physical_quantity_delta <> 0 OR reserved_quantity_delta <> 0 "
            "OR putaway_pending_quantity_delta <> 0"
        ),
    )
    op.create_check_constraint(
        "ck_inventory_balance_putaway_pending_non_negative",
        "inventory_balances",
        "putaway_pending_quantity >= 0",
    )
    op.create_check_constraint(
        "ck_inventory_balance_committed_lte_physical",
        "inventory_balances",
        "reserved_quantity + putaway_pending_quantity <= physical_quantity",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_inventory_balance_committed_lte_physical",
        "inventory_balances",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_balance_putaway_pending_non_negative",
        "inventory_balances",
        type_="check",
    )
    op.drop_constraint(
        "ck_inventory_movement_has_delta",
        "inventory_movements",
        type_="check",
    )
    op.create_check_constraint(
        "ck_inventory_movement_has_delta",
        "inventory_movements",
        "physical_quantity_delta <> 0 OR reserved_quantity_delta <> 0",
    )
    op.drop_column("inventory_movements", "putaway_pending_quantity_delta")
    op.drop_column("inventory_balances", "putaway_pending_quantity")
