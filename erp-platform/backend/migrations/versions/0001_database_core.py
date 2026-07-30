"""database core technical foundation

Revision ID: 0001_database_core
Revises:
Create Date: 2026-07-28 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op

revision: str = "0001_database_core"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')


def downgrade() -> None:
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')
