"""Add the missing audit column to inventory transfers.

Revision ID: 0027_transfer_audit_fix
Revises: 0026_menu_availability_cascade
Create Date: 2026-10-04
"""

import sqlalchemy as sa
from alembic import op


revision = "0027_transfer_audit_fix"
down_revision = "0026_menu_availability_cascade"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_transfers", sa.Column("deleted_by", sa.UUID(), nullable=True))


def downgrade() -> None:
    op.drop_column("inventory_transfers", "deleted_by")
