"""add tenant slug email uniqueness

Revision ID: 0003_auth_tenant_slug_email
Revises: 0002_authentication
Create Date: 2026-07-28 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003_auth_tenant_slug_email"
down_revision: str | None = "0002_authentication"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_auth_users_tenant_slug_email",
        "auth_users",
        ["tenant_slug", "email"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_auth_users_tenant_slug_email",
        "auth_users",
        type_="unique",
    )
