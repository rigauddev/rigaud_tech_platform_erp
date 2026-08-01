"""align authentication tenant and branch context

Revision ID: 0011_auth_tenant_alignment
Revises: 0010_product_categories
Create Date: 2026-08-01 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_auth_tenant_alignment"
down_revision: str | None = "0010_product_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("auth_users", sa.Column("active_branch_id", sa.UUID(), nullable=True))
    op.add_column("auth_users", sa.Column("role", sa.String(length=64), nullable=True))
    op.add_column(
        "auth_users",
        sa.Column(
            "permissions",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.create_foreign_key(
        "fk_auth_users_active_branch_id_branches",
        "auth_users",
        "branches",
        ["active_branch_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_auth_users_active_branch_id"), "auth_users", ["active_branch_id"])
    op.create_index(
        "uq_auth_users_email_global_active",
        "auth_users",
        [sa.text("lower(email)")],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )

    op.execute(
        """
        UPDATE auth_users AS users
        SET
            active_branch_id = branch_memberships.branch_id,
            role = branch_memberships.role
        FROM company_memberships
        JOIN branch_memberships
            ON branch_memberships.company_membership_id = company_memberships.id
           AND branch_memberships.is_default = true
           AND branch_memberships.status = 'active'
        WHERE company_memberships.user_id = users.id
          AND company_memberships.tenant_id = users.tenant_id
          AND company_memberships.status = 'active'
          AND company_memberships.is_default = true
          AND users.active_branch_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE auth_users AS users
        SET active_branch_id = branches.id,
            role = COALESCE(users.role, 'branch_operator')
        FROM branches
        WHERE branches.tenant_id = users.tenant_id
          AND branches.deleted_at IS NULL
          AND users.active_branch_id IS NULL
        """
    )

    op.create_table(
        "user_branch_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("old_branch_id", sa.UUID(), nullable=True),
        sa.Column("new_branch_id", sa.UUID(), nullable=False),
        sa.Column("changed_by", sa.UUID(), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["changed_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["new_branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["old_branch_id"], ["branches.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_user_branch_history_changed_at",
        "user_branch_history",
        ["changed_at"],
    )
    op.create_index(
        "ix_user_branch_history_tenant_user",
        "user_branch_history",
        ["tenant_id", "user_id"],
    )
    op.create_index(op.f("ix_user_branch_history_tenant_id"), "user_branch_history", ["tenant_id"])
    op.create_index(op.f("ix_user_branch_history_user_id"), "user_branch_history", ["user_id"])

    op.create_table(
        "user_work_assignments",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("assigned_by", sa.UUID(), nullable=True),
        sa.Column("reason", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["assigned_by"], ["auth_users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["auth_users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_user_work_assignments_current",
        "user_work_assignments",
        ["tenant_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("is_current = true"),
    )
    op.create_index(
        "ix_user_work_assignments_tenant_branch",
        "user_work_assignments",
        ["tenant_id", "branch_id"],
    )
    op.create_index(op.f("ix_user_work_assignments_branch_id"), "user_work_assignments", ["branch_id"])
    op.create_index(op.f("ix_user_work_assignments_tenant_id"), "user_work_assignments", ["tenant_id"])
    op.create_index(op.f("ix_user_work_assignments_user_id"), "user_work_assignments", ["user_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_user_work_assignments_user_id"), table_name="user_work_assignments")
    op.drop_index(op.f("ix_user_work_assignments_tenant_id"), table_name="user_work_assignments")
    op.drop_index(op.f("ix_user_work_assignments_branch_id"), table_name="user_work_assignments")
    op.drop_index("ix_user_work_assignments_tenant_branch", table_name="user_work_assignments")
    op.drop_index("uq_user_work_assignments_current", table_name="user_work_assignments")
    op.drop_table("user_work_assignments")
    op.drop_index(op.f("ix_user_branch_history_user_id"), table_name="user_branch_history")
    op.drop_index(op.f("ix_user_branch_history_tenant_id"), table_name="user_branch_history")
    op.drop_index("ix_user_branch_history_tenant_user", table_name="user_branch_history")
    op.drop_index("ix_user_branch_history_changed_at", table_name="user_branch_history")
    op.drop_table("user_branch_history")
    op.drop_index("uq_auth_users_email_global_active", table_name="auth_users")
    op.drop_index(op.f("ix_auth_users_active_branch_id"), table_name="auth_users")
    op.drop_constraint("fk_auth_users_active_branch_id_branches", "auth_users", type_="foreignkey")
    op.drop_column("auth_users", "permissions")
    op.drop_column("auth_users", "role")
    op.drop_column("auth_users", "active_branch_id")
