"""warehouse zones

Revision ID: 0014_warehouse_zones
Revises: 0013_warehouses
Create Date: 2026-08-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014_warehouse_zones"
down_revision: str | None = "0013_warehouses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    zone_type = postgresql.ENUM(
        "receiving",
        "shipping",
        "storage",
        "production",
        "quarantine",
        "picking",
        "display",
        "other",
        name="warehouse_zone_type",
        create_type=False,
    )
    zone_status = postgresql.ENUM(
        "active", "inactive", name="warehouse_zone_status", create_type=False
    )
    zone_type.create(op.get_bind(), checkfirst=True)
    zone_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "warehouse_zones",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("type", zone_type, nullable=False),
        sa.Column("color", sa.String(length=20), nullable=True),
        sa.Column("icon", sa.String(length=80), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_receiving", sa.Boolean(), nullable=False),
        sa.Column("is_shipping", sa.Boolean(), nullable=False),
        sa.Column("is_storage", sa.Boolean(), nullable=False),
        sa.Column("is_production", sa.Boolean(), nullable=False),
        sa.Column("is_quarantine", sa.Boolean(), nullable=False),
        sa.Column("status", zone_status, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_warehouse_zones_tenant_id"), "warehouse_zones", ["tenant_id"])
    op.create_index(op.f("ix_warehouse_zones_branch_id"), "warehouse_zones", ["branch_id"])
    op.create_index(
        op.f("ix_warehouse_zones_warehouse_id"), "warehouse_zones", ["warehouse_id"]
    )
    op.create_index(
        "uq_warehouse_zones_tenant_warehouse_code",
        "warehouse_zones",
        ["tenant_id", "warehouse_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_warehouse_zones_tenant_branch", "warehouse_zones", ["tenant_id", "branch_id"]
    )
    op.create_index(
        "ix_warehouse_zones_tenant_warehouse", "warehouse_zones", ["tenant_id", "warehouse_id"]
    )
    op.create_index(
        "ix_warehouse_zones_tenant_active", "warehouse_zones", ["tenant_id", "is_active"]
    )


def downgrade() -> None:
    op.drop_index("ix_warehouse_zones_tenant_active", table_name="warehouse_zones")
    op.drop_index("ix_warehouse_zones_tenant_warehouse", table_name="warehouse_zones")
    op.drop_index("ix_warehouse_zones_tenant_branch", table_name="warehouse_zones")
    op.drop_index("uq_warehouse_zones_tenant_warehouse_code", table_name="warehouse_zones")
    op.drop_index(op.f("ix_warehouse_zones_warehouse_id"), table_name="warehouse_zones")
    op.drop_index(op.f("ix_warehouse_zones_branch_id"), table_name="warehouse_zones")
    op.drop_index(op.f("ix_warehouse_zones_tenant_id"), table_name="warehouse_zones")
    op.drop_table("warehouse_zones")
    sa.Enum(name="warehouse_zone_status").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="warehouse_zone_type").drop(op.get_bind(), checkfirst=True)
