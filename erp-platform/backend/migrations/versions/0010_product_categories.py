"""add product categories

Revision ID: 0010_product_categories
Revises: 0009_tenant_context
Create Date: 2026-07-31 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0010_product_categories"
down_revision: str | None = "0009_tenant_context"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    category_status = postgresql.ENUM(
        "active", "inactive", name="category_status", create_type=False
    )
    category_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("parent_id", sa.UUID(), nullable=True),
        sa.Column("internal_code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("icon", sa.String(length=80), nullable=True),
        sa.Column("color", sa.String(length=7), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.Column("status", category_status, nullable=False),
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
        sa.CheckConstraint(
            "display_order >= 0",
            name="ck_categories_display_order_non_negative",
        ),
        sa.ForeignKeyConstraint(["parent_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id",
            "internal_code",
            name="uq_categories_tenant_id_internal_code",
        ),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_categories_tenant_id_slug"),
    )
    op.create_index(op.f("ix_categories_tenant_id"), "categories", ["tenant_id"])
    op.create_index("ix_categories_tenant_parent", "categories", ["tenant_id", "parent_id"])
    op.create_index("ix_categories_tenant_status", "categories", ["tenant_id", "status"])
    op.create_index(
        "ix_categories_tenant_order",
        "categories",
        ["tenant_id", "display_order", "name"],
    )


def downgrade() -> None:
    op.drop_index("ix_categories_tenant_order", table_name="categories")
    op.drop_index("ix_categories_tenant_status", table_name="categories")
    op.drop_index("ix_categories_tenant_parent", table_name="categories")
    op.drop_index(op.f("ix_categories_tenant_id"), table_name="categories")
    op.drop_table("categories")
    sa.Enum(name="category_status").drop(op.get_bind(), checkfirst=True)
