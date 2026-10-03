"""inventory engine

Revision ID: 0012_inventory_engine
Revises: 0011_auth_tenant_alignment
Create Date: 2026-08-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0012_inventory_engine"
down_revision: str | None = "0011_auth_tenant_alignment"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    movement_type = postgresql.ENUM(
        "adjustment_in",
        "adjustment_out",
        "reservation_created",
        "reservation_released",
        name="inventory_movement_type",
        create_type=False,
    )
    movement_status = postgresql.ENUM(
        "confirmed", name="inventory_movement_status", create_type=False
    )
    adjustment_type = postgresql.ENUM(
        "increase", "decrease", name="inventory_adjustment_type", create_type=False
    )
    adjustment_status = postgresql.ENUM(
        "confirmed", name="inventory_adjustment_status", create_type=False
    )
    reservation_status = postgresql.ENUM(
        "active", "released", "cancelled", name="inventory_reservation_status", create_type=False
    )
    for enum in (
        movement_type,
        movement_status,
        adjustment_type,
        adjustment_status,
        reservation_status,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "inventory_balances",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column(
            "physical_quantity",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "reserved_quantity",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.CheckConstraint(
            "physical_quantity >= 0",
            name="ck_inventory_balance_physical_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity >= 0",
            name="ck_inventory_balance_reserved_non_negative",
        ),
        sa.CheckConstraint(
            "reserved_quantity <= physical_quantity",
            name="ck_inventory_balance_reserved_lte_physical",
        ),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_balances_tenant_id"), "inventory_balances", ["tenant_id"])
    op.create_index(
        "uq_inventory_balances_scope",
        "inventory_balances",
        ["tenant_id", "branch_id", "product_id", "warehouse_id", "location_id"],
        unique=True,
        postgresql_nulls_not_distinct=True,
    )
    op.create_index(
        "ix_inventory_balances_tenant_branch",
        "inventory_balances",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_inventory_balances_tenant_product",
        "inventory_balances",
        ["tenant_id", "product_id"],
    )

    op.create_table(
        "inventory_movements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("movement_type", movement_type, nullable=False),
        sa.Column("status", movement_status, nullable=False),
        sa.Column(
            "physical_quantity_delta",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column(
            "reserved_quantity_delta",
            sa.Numeric(precision=14, scale=3),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=True),
        sa.Column("source_id", sa.UUID(), nullable=True),
        sa.Column("event_name", sa.String(length=120), nullable=False),
        sa.Column("actor_id", sa.UUID(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "physical_quantity_delta <> 0 OR reserved_quantity_delta <> 0",
            name="ck_inventory_movement_has_delta",
        ),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_inventory_movements_tenant_id"), "inventory_movements", ["tenant_id"])
    op.create_index(
        "ix_inventory_movements_tenant_branch",
        "inventory_movements",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_inventory_movements_tenant_product",
        "inventory_movements",
        ["tenant_id", "product_id"],
    )
    op.create_index(
        "ix_inventory_movements_tenant_type",
        "inventory_movements",
        ["tenant_id", "movement_type"],
    )
    op.create_index(
        "ix_inventory_movements_source",
        "inventory_movements",
        ["source_module", "source_id"],
    )

    op.create_table(
        "inventory_adjustments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("movement_id", sa.UUID(), nullable=True),
        sa.Column("warehouse_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("adjustment_type", adjustment_type, nullable=False),
        sa.Column("status", adjustment_status, nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("created_by", sa.UUID(), nullable=True),
        sa.Column("updated_by", sa.UUID(), nullable=True),
        sa.Column("deleted_by", sa.UUID(), nullable=True),
        sa.CheckConstraint("quantity > 0", name="ck_inventory_adjustment_quantity_positive"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["movement_id"], ["inventory_movements.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_inventory_adjustments_tenant_id"), "inventory_adjustments", ["tenant_id"]
    )
    op.create_index(
        "ix_inventory_adjustments_tenant_branch",
        "inventory_adjustments",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_inventory_adjustments_tenant_product",
        "inventory_adjustments",
        ["tenant_id", "product_id"],
    )

    op.create_table(
        "inventory_reservations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=True),
        sa.Column("location_id", sa.UUID(), nullable=True),
        sa.Column("status", reservation_status, nullable=False),
        sa.Column("quantity", sa.Numeric(precision=14, scale=3), nullable=False),
        sa.Column("reason", sa.String(length=240), nullable=False),
        sa.Column("source_module", sa.String(length=80), nullable=True),
        sa.Column("source_id", sa.UUID(), nullable=True),
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
        sa.CheckConstraint("quantity > 0", name="ck_inventory_reservation_quantity_positive"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_inventory_reservations_tenant_id"), "inventory_reservations", ["tenant_id"]
    )
    op.create_index(
        "ix_inventory_reservations_tenant_branch",
        "inventory_reservations",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_inventory_reservations_tenant_product",
        "inventory_reservations",
        ["tenant_id", "product_id"],
    )
    op.create_index(
        "ix_inventory_reservations_tenant_status",
        "inventory_reservations",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_inventory_reservations_source",
        "inventory_reservations",
        ["source_module", "source_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_reservations_source", table_name="inventory_reservations")
    op.drop_index("ix_inventory_reservations_tenant_status", table_name="inventory_reservations")
    op.drop_index("ix_inventory_reservations_tenant_product", table_name="inventory_reservations")
    op.drop_index("ix_inventory_reservations_tenant_branch", table_name="inventory_reservations")
    op.drop_index(op.f("ix_inventory_reservations_tenant_id"), table_name="inventory_reservations")
    op.drop_table("inventory_reservations")

    op.drop_index("ix_inventory_adjustments_tenant_product", table_name="inventory_adjustments")
    op.drop_index("ix_inventory_adjustments_tenant_branch", table_name="inventory_adjustments")
    op.drop_index(op.f("ix_inventory_adjustments_tenant_id"), table_name="inventory_adjustments")
    op.drop_table("inventory_adjustments")

    op.drop_index("ix_inventory_movements_source", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_tenant_type", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_tenant_product", table_name="inventory_movements")
    op.drop_index("ix_inventory_movements_tenant_branch", table_name="inventory_movements")
    op.drop_index(op.f("ix_inventory_movements_tenant_id"), table_name="inventory_movements")
    op.drop_table("inventory_movements")

    op.drop_index("ix_inventory_balances_tenant_product", table_name="inventory_balances")
    op.drop_index("ix_inventory_balances_tenant_branch", table_name="inventory_balances")
    op.drop_index("uq_inventory_balances_scope", table_name="inventory_balances")
    op.drop_index(op.f("ix_inventory_balances_tenant_id"), table_name="inventory_balances")
    op.drop_table("inventory_balances")

    for enum_name in (
        "inventory_reservation_status",
        "inventory_adjustment_status",
        "inventory_adjustment_type",
        "inventory_movement_status",
        "inventory_movement_type",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
