"""add products

Revision ID: 0008_products
Revises: 0007_mfa_2fa
Create Date: 2026-07-30 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0008_products"
down_revision: str | None = "0007_mfa_2fa"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    product_type = postgresql.ENUM(
        "simple", "service", "prepared_item", name="product_type", create_type=False
    )
    unit_of_measure = postgresql.ENUM(
        "unit",
        "kg",
        "g",
        "l",
        "ml",
        "portion",
        name="product_unit_of_measure",
        create_type=False,
    )
    product_status = postgresql.ENUM("active", "inactive", name="product_status", create_type=False)
    product_type.create(op.get_bind(), checkfirst=True)
    unit_of_measure.create(op.get_bind(), checkfirst=True)
    product_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "products",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("internal_code", sa.String(length=40), nullable=False),
        sa.Column("barcode", sa.String(length=64), nullable=True),
        sa.Column("product_type", product_type, nullable=False),
        sa.Column("unit_of_measure", unit_of_measure, nullable=False),
        sa.Column("status", product_status, nullable=False),
        sa.Column("sale_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("cost_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("main_image_url", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_available_for_sale", sa.Boolean(), nullable=False),
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
        sa.CheckConstraint("sale_price >= 0", name="ck_products_sale_price_non_negative"),
        sa.CheckConstraint("cost_price >= 0", name="ck_products_cost_price_non_negative"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "internal_code",
            name="uq_products_tenant_id_internal_code",
        ),
    )
    op.create_index(op.f("ix_products_tenant_id"), "products", ["tenant_id"])
    op.create_index("ix_products_tenant_active", "products", ["tenant_id", "is_active"])
    op.create_index("ix_products_tenant_status", "products", ["tenant_id", "status"])
    op.create_index(
        "ix_products_tenant_available",
        "products",
        ["tenant_id", "is_available_for_sale"],
    )
    op.create_index("ix_products_tenant_type", "products", ["tenant_id", "product_type"])
    op.create_index(
        "uq_products_tenant_id_barcode_not_null",
        "products",
        ["tenant_id", "barcode"],
        unique=True,
        postgresql_where=sa.text("barcode IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_products_tenant_id_barcode_not_null", table_name="products")
    op.drop_index("ix_products_tenant_type", table_name="products")
    op.drop_index("ix_products_tenant_available", table_name="products")
    op.execute("DROP INDEX IF EXISTS ix_products_tenant_status")
    op.drop_index("ix_products_tenant_active", table_name="products")
    op.drop_index(op.f("ix_products_tenant_id"), table_name="products")
    op.drop_table("products")

    sa.Enum(name="product_unit_of_measure").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="product_type").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="product_status").drop(op.get_bind(), checkfirst=True)
