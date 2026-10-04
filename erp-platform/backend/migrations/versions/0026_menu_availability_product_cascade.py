"""Cascade physical product cleanup to commercial menu availability.

Revision ID: 0026_menu_availability_cascade
Revises: 0025_menu_availability
Create Date: 2026-10-03
"""

from alembic import op


revision = "0026_menu_availability_cascade"
down_revision = "0025_menu_availability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "fk_restaurant_menu_availabilities_product_id_products",
        "restaurant_menu_availabilities",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_restaurant_menu_availabilities_product_id_products",
        "restaurant_menu_availabilities",
        "products",
        ["product_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_restaurant_menu_availabilities_product_id_products",
        "restaurant_menu_availabilities",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "fk_restaurant_menu_availabilities_product_id_products",
        "restaurant_menu_availabilities",
        "products",
        ["product_id"],
        ["id"],
        ondelete="RESTRICT",
    )
