"""stock adjustments governance

Revision ID: 0020_stock_adjustments
Revises: 0019_inventory_count
Create Date: 2026-10-03 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020_stock_adjustments"
down_revision: str | None = "0019_inventory_count"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    reason = sa.Enum("correction", "damage", "loss", "expiry", "opening_balance", "return", "reversal", name="inventory_adjustment_reason")
    reason.create(op.get_bind(), checkfirst=True)
    op.add_column("inventory_adjustments", sa.Column("reason_code", reason, nullable=False, server_default="correction"))
    op.add_column("inventory_adjustments", sa.Column("reversal_of_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_inventory_adjustments_reversal", "inventory_adjustments", "inventory_adjustments", ["reversal_of_id"], ["id"], ondelete="RESTRICT")
    op.create_index("ix_inventory_adjustments_reversal", "inventory_adjustments", ["reversal_of_id"])


def downgrade() -> None:
    op.drop_index("ix_inventory_adjustments_reversal", table_name="inventory_adjustments")
    op.drop_constraint("fk_inventory_adjustments_reversal", "inventory_adjustments", type_="foreignkey")
    op.drop_column("inventory_adjustments", "reversal_of_id")
    op.drop_column("inventory_adjustments", "reason_code")
    sa.Enum(name="inventory_adjustment_reason").drop(op.get_bind(), checkfirst=True)
