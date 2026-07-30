"""tenant memberships branches context

Revision ID: 0009_tenant_context
Revises: 0008_products
Create Date: 2026-07-30 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_tenant_context"
down_revision: str | None = "0008_products"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    branch_type = postgresql.ENUM(
        "headquarters", "store", "warehouse", name="branch_type", create_type=False
    )
    branch_status = postgresql.ENUM("active", "inactive", name="branch_status", create_type=False)
    membership_status = postgresql.ENUM(
        "active", "inactive", name="membership_status", create_type=False
    )
    branch_membership_status = postgresql.ENUM(
        "active", "inactive", name="branch_membership_status", create_type=False
    )
    company_role = postgresql.ENUM(
        "company_admin", "member", name="company_role", create_type=False
    )
    branch_role = postgresql.ENUM(
        "branch_manager", "branch_operator", name="branch_role", create_type=False
    )
    access_scope = postgresql.ENUM(
        "all_branches", "selected_branches", name="access_scope", create_type=False
    )
    for enum in (
        branch_type,
        branch_status,
        membership_status,
        branch_membership_status,
        company_role,
        branch_role,
        access_scope,
    ):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "branches",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("code", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("legal_name", sa.String(length=180), nullable=True),
        sa.Column("trade_name", sa.String(length=120), nullable=True),
        sa.Column("document", sa.String(length=14), nullable=True),
        sa.Column("branch_type", branch_type, nullable=False),
        sa.Column("status", branch_status, nullable=False),
        sa.Column("is_headquarters", sa.Boolean(), nullable=False),
        sa.Column("timezone", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("address", sa.String(length=500), nullable=True),
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
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_branches_tenant_id_code"),
    )
    op.create_index(op.f("ix_branches_tenant_id"), "branches", ["tenant_id"])
    op.create_index(
        "uq_branches_tenant_id_document_not_null",
        "branches",
        ["tenant_id", "document"],
        unique=True,
        postgresql_where=sa.text("document IS NOT NULL"),
    )
    op.create_index(
        "uq_branches_tenant_id_headquarters",
        "branches",
        ["tenant_id"],
        unique=True,
        postgresql_where=sa.text("is_headquarters = true AND deleted_at IS NULL"),
    )

    op.create_table(
        "company_memberships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("role", company_role, nullable=False),
        sa.Column("status", membership_status, nullable=False),
        sa.Column("access_scope", access_scope, nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "tenant_id", name="uq_company_memberships_user_tenant"),
    )
    op.create_index(op.f("ix_company_memberships_tenant_id"), "company_memberships", ["tenant_id"])
    op.create_index(op.f("ix_company_memberships_user_id"), "company_memberships", ["user_id"])
    op.create_index(
        "uq_company_memberships_user_default",
        "company_memberships",
        ["user_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    op.create_table(
        "branch_memberships",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("company_membership_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("role", branch_role, nullable=False),
        sa.Column("status", branch_membership_status, nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["company_membership_id"], ["company_memberships.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "company_membership_id",
            "branch_id",
            name="uq_branch_memberships_company_membership_branch",
        ),
    )
    op.create_index(op.f("ix_branch_memberships_branch_id"), "branch_memberships", ["branch_id"])
    op.create_index(
        op.f("ix_branch_memberships_company_membership_id"),
        "branch_memberships",
        ["company_membership_id"],
    )
    op.create_index(
        "uq_branch_memberships_company_membership_default",
        "branch_memberships",
        ["company_membership_id"],
        unique=True,
        postgresql_where=sa.text("is_default = true"),
    )

    op.add_column("auth_sessions", sa.Column("membership_id", sa.UUID(), nullable=True))
    op.add_column("auth_sessions", sa.Column("branch_id", sa.UUID(), nullable=True))
    op.add_column("auth_sessions", sa.Column("branch_membership_id", sa.UUID(), nullable=True))
    op.add_column("auth_sessions", sa.Column("role", sa.String(length=64), nullable=True))
    op.add_column("auth_sessions", sa.Column("access_scope", sa.String(length=64), nullable=True))
    op.create_index("ix_auth_sessions_membership_id", "auth_sessions", ["membership_id"])
    op.create_index("ix_auth_sessions_branch_id", "auth_sessions", ["branch_id"])

    _backfill_default_context()


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_branch_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_membership_id", table_name="auth_sessions")
    op.drop_column("auth_sessions", "access_scope")
    op.drop_column("auth_sessions", "role")
    op.drop_column("auth_sessions", "branch_membership_id")
    op.drop_column("auth_sessions", "branch_id")
    op.drop_column("auth_sessions", "membership_id")

    op.drop_index(
        "uq_branch_memberships_company_membership_default", table_name="branch_memberships"
    )
    op.drop_index(
        op.f("ix_branch_memberships_company_membership_id"), table_name="branch_memberships"
    )
    op.drop_index(op.f("ix_branch_memberships_branch_id"), table_name="branch_memberships")
    op.drop_table("branch_memberships")

    op.drop_index("uq_company_memberships_user_default", table_name="company_memberships")
    op.drop_index(op.f("ix_company_memberships_user_id"), table_name="company_memberships")
    op.drop_index(op.f("ix_company_memberships_tenant_id"), table_name="company_memberships")
    op.drop_table("company_memberships")

    op.drop_index("uq_branches_tenant_id_headquarters", table_name="branches")
    op.drop_index("uq_branches_tenant_id_document_not_null", table_name="branches")
    op.drop_index(op.f("ix_branches_tenant_id"), table_name="branches")
    op.drop_table("branches")

    for enum_name in (
        "access_scope",
        "branch_role",
        "company_role",
        "branch_membership_status",
        "membership_status",
        "branch_status",
        "branch_type",
    ):
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)


def _backfill_default_context() -> None:
    op.execute(
        """
        INSERT INTO branches (
            id, tenant_id, code, name, legal_name, trade_name, document, branch_type, status,
            is_headquarters, timezone, phone, email, created_at, updated_at
        )
        SELECT
            gen_random_uuid(), id, 'HQ', trade_name, legal_name, trade_name, document,
            'headquarters'::branch_type, 'active'::branch_status,
            true, timezone, phone, email, now(), now()
        FROM companies
        WHERE deleted_at IS NULL
        ON CONFLICT (tenant_id, code) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO company_memberships (
            id, user_id, tenant_id, role, status, access_scope, is_default, created_at, updated_at
        )
        SELECT
            gen_random_uuid(), id, tenant_id,
            CASE
                WHEN is_superuser THEN 'company_admin'::company_role
                ELSE 'member'::company_role
            END,
            'active'::membership_status,
            CASE
                WHEN is_superuser THEN 'all_branches'::access_scope
                ELSE 'selected_branches'::access_scope
            END,
            true,
            now(),
            now()
        FROM auth_users
        WHERE deleted_at IS NULL
        ON CONFLICT (user_id, tenant_id) DO NOTHING
        """
    )
    op.execute(
        """
        INSERT INTO branch_memberships (
            id, company_membership_id, branch_id, role, status, is_default, created_at, updated_at
        )
        SELECT
            gen_random_uuid(), cm.id, b.id,
            CASE
                WHEN cm.role = 'company_admin' THEN 'branch_manager'::branch_role
                ELSE 'branch_operator'::branch_role
            END,
            'active'::branch_membership_status,
            true,
            now(),
            now()
        FROM company_memberships cm
        JOIN branches b ON b.tenant_id = cm.tenant_id AND b.is_headquarters = true
        ON CONFLICT (company_membership_id, branch_id) DO NOTHING
        """
    )
