"""restaurant menu availability

Revision ID: 0025_menu_availability
Revises: 0024_restaurant_staff
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0025_menu_availability"
down_revision: str | None = "0024_restaurant_staff"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "DO $$ BEGIN CREATE TYPE restaurant_menu_availability_status AS ENUM ('published', 'unavailable'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;"
    )
    status = postgresql.ENUM(
        "published", "unavailable", name="restaurant_menu_availability_status", create_type=False
    )
    op.create_table(
        "restaurant_menu_availabilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("service_date", sa.Date(), nullable=False),
        sa.Column("service_period", sa.String(length=40), nullable=False),
        sa.Column("channels", sa.JSON(), nullable=False),
        sa.Column("available_quantity", sa.Integer(), nullable=True),
        sa.Column("sold_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", status, nullable=False, server_default="published"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint(
            "available_quantity IS NULL OR available_quantity >= 0",
            name="restaurant_menu_availability_quantity_nonnegative",
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_restaurant_menu_availability_scope",
        "restaurant_menu_availabilities",
        ["tenant_id", "branch_id", "product_id", "service_date", "service_period"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_restaurant_menu_availability_tenant_branch_date",
        "restaurant_menu_availabilities",
        ["tenant_id", "branch_id", "service_date"],
    )


def downgrade() -> None:
    op.drop_table("restaurant_menu_availabilities")
    sa.Enum(name="restaurant_menu_availability_status").drop(op.get_bind(), checkfirst=True)
