"""receiving documents

Revision ID: 0016_receiving_documents
Revises: 0015_warehouse_locations
Create Date: 2026-08-02 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016_receiving_documents"
down_revision: str | None = "0015_warehouse_locations"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    document_status = postgresql.ENUM(
        "draft",
        "expected",
        "receiving",
        "partial",
        "received",
        "cancelled",
        name="receiving_document_status",
        create_type=False,
    )
    document_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "receiving_documents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("branch_id", sa.UUID(), nullable=False),
        sa.Column("warehouse_id", sa.UUID(), nullable=False),
        sa.Column("supplier_id", sa.UUID(), nullable=True),
        sa.Column("document_number", sa.String(length=60), nullable=False),
        sa.Column("document_type", sa.String(length=40), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("expected_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["warehouse_id"], ["warehouses.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "receiving_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("document_id", sa.UUID(), nullable=False),
        sa.Column("product_id", sa.UUID(), nullable=False),
        sa.Column("ordered_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("received_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("damaged_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("pending_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "ordered_quantity >= 0", name="ck_receiving_item_ordered_non_negative"
        ),
        sa.CheckConstraint(
            "received_quantity >= 0", name="ck_receiving_item_received_non_negative"
        ),
        sa.CheckConstraint(
            "damaged_quantity >= 0", name="ck_receiving_item_damaged_non_negative"
        ),
        sa.CheckConstraint(
            "pending_quantity >= 0", name="ck_receiving_item_pending_non_negative"
        ),
        sa.CheckConstraint("unit_cost >= 0", name="ck_receiving_item_unit_cost_non_negative"),
        sa.ForeignKeyConstraint(["document_id"], ["receiving_documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["tenant_id"], ["companies.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_receiving_documents_tenant_branch_number",
        "receiving_documents",
        ["tenant_id", "branch_id", "document_number"],
        unique=True,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )
    op.create_index(
        "ix_receiving_documents_tenant_branch",
        "receiving_documents",
        ["tenant_id", "branch_id"],
    )
    op.create_index(
        "ix_receiving_documents_tenant_warehouse",
        "receiving_documents",
        ["tenant_id", "warehouse_id"],
    )
    op.create_index(
        "ix_receiving_documents_tenant_status",
        "receiving_documents",
        ["tenant_id", "status"],
    )
    op.create_index(
        "ix_receiving_items_tenant_document",
        "receiving_items",
        ["tenant_id", "document_id"],
    )
    op.create_index(
        "ix_receiving_items_tenant_product",
        "receiving_items",
        ["tenant_id", "product_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_receiving_items_tenant_product", table_name="receiving_items")
    op.drop_index("ix_receiving_items_tenant_document", table_name="receiving_items")
    op.drop_index("ix_receiving_documents_tenant_status", table_name="receiving_documents")
    op.drop_index("ix_receiving_documents_tenant_warehouse", table_name="receiving_documents")
    op.drop_index("ix_receiving_documents_tenant_branch", table_name="receiving_documents")
    op.drop_index(
        "uq_receiving_documents_tenant_branch_number",
        table_name="receiving_documents",
    )
    op.drop_table("receiving_items")
    op.drop_table("receiving_documents")
    sa.Enum(name="receiving_document_status").drop(op.get_bind(), checkfirst=True)
