"""warehouses

Revision ID: 0013_warehouses
Revises: 0012_inventory_engine
Create Date: 2026-08-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0013_warehouses"
down_revision: str | None = "0012_inventory_engine"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    warehouse_status = postgresql.ENUM(
        "active", "inactive", name="warehouse_status", create_type=False
    )
    warehouse_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "warehouses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
        sa.Column("status", warehouse_status, nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_warehouses_tenant_id"), "warehouses", ["tenant_id"])
    op.create_index(op.f("ix_warehouses_branch_id"), "warehouses", ["branch_id"])
    op.create_index(
        "uq_warehouses_tenant_branch_code",
        "warehouses",
        ["tenant_id", "branch_id", "code"],
        unique=True,
    )
    op.create_index(
        "uq_warehouses_tenant_branch_default",
        "warehouses",
        ["tenant_id", "branch_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true AND deleted_at IS NULL"),
    )
    op.create_index("ix_warehouses_tenant_branch", "warehouses", ["tenant_id", "branch_id"])
    op.create_index("ix_warehouses_tenant_active", "warehouses", ["tenant_id", "is_active"])

    for table_name in (
        "inventory_balances",
        "inventory_movements",
        "inventory_adjustments",
        "inventory_reservations",
    ):
        op.create_foreign_key(
            f"fk_{table_name}_warehouse_id_warehouses",
            table_name,
            "warehouses",
            ["warehouse_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    for table_name in (
        "inventory_reservations",
        "inventory_adjustments",
        "inventory_movements",
        "inventory_balances",
    ):
        op.drop_constraint(
            f"fk_{table_name}_warehouse_id_warehouses",
            table_name,
            type_="foreignkey",
        )

    op.drop_index("ix_warehouses_tenant_active", table_name="warehouses")
    op.drop_index("ix_warehouses_tenant_branch", table_name="warehouses")
    op.drop_index("uq_warehouses_tenant_branch_default", table_name="warehouses")
    op.drop_index("uq_warehouses_tenant_branch_code", table_name="warehouses")
    op.drop_index(op.f("ix_warehouses_branch_id"), table_name="warehouses")
    op.drop_index(op.f("ix_warehouses_tenant_id"), table_name="warehouses")
    op.drop_table("warehouses")
    sa.Enum(name="warehouse_status").drop(op.get_bind(), checkfirst=True)
