"""create companies tenant root

Revision ID: 0004_companies
Revises: 0003_auth_tenant_slug_email
Create Date: 2026-07-28 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004_companies"
down_revision: str | None = "0003_auth_tenant_slug_email"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

company_status = postgresql.ENUM(
    "active",
    "inactive",
    "suspended",
    name="company_status",
    create_type=False,
)


def upgrade() -> None:
    company_status.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("legal_name", sa.String(length=180), nullable=False),
        sa.Column("trade_name", sa.String(length=120), nullable=False),
        sa.Column("document", sa.String(length=14), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("slug", sa.String(length=80), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("status", company_status, nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("locale", sa.String(length=16), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("updated_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("deleted_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name="pk_companies"),
        sa.UniqueConstraint("document", name="uq_companies_document"),
        sa.UniqueConstraint("slug", name="uq_companies_slug"),
        sa.UniqueConstraint("code", name="uq_companies_code"),
        sa.CheckConstraint("char_length(document) = 14", name="ck_companies_document_len"),
        sa.CheckConstraint(
            "status in ('active', 'inactive', 'suspended')",
            name="ck_companies_status",
        ),
    )
    op.create_index("ix_companies_slug", "companies", ["slug"])
    op.create_index("ix_companies_code", "companies", ["code"])
    op.create_index("ix_companies_status", "companies", ["status"])
    op.create_index("ix_companies_is_active", "companies", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_companies_is_active", table_name="companies")
    op.drop_index("ix_companies_status", table_name="companies")
    op.drop_index("ix_companies_code", table_name="companies")
    op.drop_index("ix_companies_slug", table_name="companies")
    op.drop_table("companies")
    company_status.drop(op.get_bind(), checkfirst=True)
