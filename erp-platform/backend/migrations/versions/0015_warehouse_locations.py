"""warehouse locations

Revision ID: 0015_warehouse_locations
Revises: 0014_warehouse_zones
Create Date: 2026-08-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0015_warehouse_locations"
down_revision: str | None = "0014_warehouse_zones"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    location_status = postgresql.ENUM(
        "active", "inactive", name="warehouse_location_status", create_type=False
    )
    location_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "warehouse_locations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("zone_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("alias", sa.String(length=80), nullable=True),
        sa.Column("barcode", sa.String(length=80), nullable=True),
        sa.Column("qr_code", sa.String(length=160), nullable=True),
        sa.Column("aisle", sa.String(length=40), nullable=True),
        sa.Column("rack", sa.String(length=40), nullable=True),
        sa.Column("shelf", sa.String(length=40), nullable=True),
        sa.Column("level", sa.String(length=40), nullable=True),
        sa.Column("position", sa.String(length=40), nullable=True),
        sa.Column("capacity", sa.Numeric(14, 3), nullable=True),
        sa.Column("capacity_unit", sa.String(length=20), nullable=True),
        sa.Column("allow_negative", sa.Boolean(), nullable=False),
        sa.Column("allow_mixed_items", sa.Boolean(), nullable=False),
        sa.Column("allow_expired", sa.Boolean(), nullable=False),
        sa.Column("is_pick_location", sa.Boolean(), nullable=False),
        sa.Column("is_receive_location", sa.Boolean(), nullable=False),
        sa.Column("is_shipping_location", sa.Boolean(), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("status", location_status, nullable=False),
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
        sa.CheckConstraint("capacity IS NULL OR capacity >= 0", name="ck_warehouse_location_capacity_non_negative"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["zone_id"], ["warehouse_zones.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_warehouse_locations_tenant_id"), "warehouse_locations", ["tenant_id"])
    op.create_index(op.f("ix_warehouse_locations_branch_id"), "warehouse_locations", ["branch_id"])
    op.create_index(
        op.f("ix_warehouse_locations_warehouse_id"),
        "warehouse_locations",
        ["warehouse_id"],
    )
    op.create_index(op.f("ix_warehouse_locations_zone_id"), "warehouse_locations", ["zone_id"])
    op.create_index(
        "uq_warehouse_locations_tenant_warehouse_code",
        "warehouse_locations",
        ["tenant_id", "warehouse_id", "code"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "uq_warehouse_locations_tenant_barcode",
        "warehouse_locations",
        ["tenant_id", "barcode"],
        unique=True,
        postgresql_where=sa.text("barcode IS NOT NULL AND deleted_at IS NULL"),
    )
    op.create_index(
        "uq_warehouse_locations_tenant_qr_code",
        "warehouse_locations",
        ["tenant_id", "qr_code"],
        unique=True,
        postgresql_where=sa.text("qr_code IS NOT NULL AND deleted_at IS NULL"),
    )
    op.create_index(
        "ix_warehouse_locations_tenant_branch",
        "warehouse_locations",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_warehouse_locations_tenant_warehouse",
        "warehouse_locations",
        ["tenant_id", "warehouse_id"],
    )
    op.create_index(
        "ix_warehouse_locations_tenant_zone",
        "warehouse_locations",
        ["tenant_id", "zone_id"],
    )
    op.create_index(
        "ix_warehouse_locations_tenant_active",
        "warehouse_locations",
        ["tenant_id", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("ix_warehouse_locations_tenant_active", table_name="warehouse_locations")
    op.drop_index("ix_warehouse_locations_tenant_zone", table_name="warehouse_locations")
    op.drop_index("ix_warehouse_locations_tenant_warehouse", table_name="warehouse_locations")
    op.drop_index("ix_warehouse_locations_tenant_branch", table_name="warehouse_locations")
    op.drop_index("uq_warehouse_locations_tenant_qr_code", table_name="warehouse_locations")
    op.drop_index("uq_warehouse_locations_tenant_barcode", table_name="warehouse_locations")
    op.drop_index("uq_warehouse_locations_tenant_warehouse_code", table_name="warehouse_locations")
    op.drop_index(op.f("ix_warehouse_locations_zone_id"), table_name="warehouse_locations")
    op.drop_index(op.f("ix_warehouse_locations_warehouse_id"), table_name="warehouse_locations")
    op.drop_index(op.f("ix_warehouse_locations_branch_id"), table_name="warehouse_locations")
    op.drop_index(op.f("ix_warehouse_locations_tenant_id"), table_name="warehouse_locations")
    op.drop_table("warehouse_locations")
    sa.Enum(name="warehouse_location_status").drop(op.get_bind(), checkfirst=True)
