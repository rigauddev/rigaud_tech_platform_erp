from uuid import UUID, uuid4

from sqlalchemy import Boolean, Enum, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.database.mixins import AuditMixin, SoftDeleteMixin, TimestampMixin
from app.database.types import UUIDType
from app.modules.companies.domain.entities import (
    AccessScope,
    BranchRole,
    BranchStatus,
    BranchType,
    CompanyRole,
    CompanyStatus,
    MembershipStatus,
)


class CompanyModel(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (
        UniqueConstraint("document", name="uq_companies_document"),
        UniqueConstraint("slug", name="uq_companies_slug"),
        UniqueConstraint("code", name="uq_companies_code"),
    )

    id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    legal_name: Mapped[str] = mapped_column(String(180), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(120), nullable=False)
    document: Mapped[str] = mapped_column(String(14), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    slug: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    status: Mapped[CompanyStatus] = mapped_column(
        Enum(
            CompanyStatus,
            name="company_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=CompanyStatus.ACTIVE,
        nullable=False,
    )
    timezone: Mapped[str] = mapped_column(String(64), default="America/Sao_Paulo", nullable=False)
    locale: Mapped[str] = mapped_column(String(16), default="pt-BR", nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="BRL", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    def activate(self) -> None:
        self.status = CompanyStatus.ACTIVE
        self.is_active = True

    def deactivate(self) -> None:
        self.status = CompanyStatus.INACTIVE
        self.is_active = False

    def suspend(self) -> None:
        self.status = CompanyStatus.SUSPENDED
        self.is_active = False


class BranchModel(TimestampMixin, SoftDeleteMixin, AuditMixin, Base):
    __tablename__ = "branches"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uq_branches_tenant_id_code"),
        Index(
            "uq_branches_tenant_id_document_not_null",
            "tenant_id",
            "document",
            unique=True,
            postgresql_where=text("document IS NOT NULL"),
        ),
        Index(
            "uq_branches_tenant_id_headquarters",
            "tenant_id",
            unique=True,
            postgresql_where=text("is_headquarters = true AND deleted_at IS NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(180), nullable=True)
    trade_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    document: Mapped[str | None] = mapped_column(String(14), nullable=True)
    branch_type: Mapped[BranchType] = mapped_column(
        Enum(BranchType, name="branch_type", values_callable=lambda enum: [e.value for e in enum]),
        default=BranchType.STORE,
        nullable=False,
    )
    status: Mapped[BranchStatus] = mapped_column(
        Enum(
            BranchStatus,
            name="branch_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=BranchStatus.ACTIVE,
        nullable=False,
    )
    is_headquarters: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), default="America/Sao_Paulo", nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)


class CompanyMembershipModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "company_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "tenant_id", name="uq_company_memberships_user_tenant"),
        Index(
            "uq_company_memberships_user_default",
            "user_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("auth_users.id", ondelete="CASCADE"), index=True
    )
    tenant_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[CompanyRole] = mapped_column(
        Enum(
            CompanyRole, name="company_role", values_callable=lambda enum: [e.value for e in enum]
        ),
        default=CompanyRole.MEMBER,
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(
            MembershipStatus,
            name="membership_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=MembershipStatus.ACTIVE,
        nullable=False,
    )
    access_scope: Mapped[AccessScope] = mapped_column(
        Enum(
            AccessScope, name="access_scope", values_callable=lambda enum: [e.value for e in enum]
        ),
        default=AccessScope.SELECTED_BRANCHES,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class BranchMembershipModel(TimestampMixin, AuditMixin, Base):
    __tablename__ = "branch_memberships"
    __table_args__ = (
        UniqueConstraint(
            "company_membership_id",
            "branch_id",
            name="uq_branch_memberships_company_membership_branch",
        ),
        Index(
            "uq_branch_memberships_company_membership_default",
            "company_membership_id",
            unique=True,
            postgresql_where=text("is_default = true"),
        ),
    )

    id: Mapped[UUID] = mapped_column(UUIDType(as_uuid=True), primary_key=True, default=uuid4)
    company_membership_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True),
        ForeignKey("company_memberships.id", ondelete="CASCADE"),
        index=True,
    )
    branch_id: Mapped[UUID] = mapped_column(
        UUIDType(as_uuid=True), ForeignKey("branches.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[BranchRole] = mapped_column(
        Enum(BranchRole, name="branch_role", values_callable=lambda enum: [e.value for e in enum]),
        default=BranchRole.BRANCH_OPERATOR,
        nullable=False,
    )
    status: Mapped[MembershipStatus] = mapped_column(
        Enum(
            MembershipStatus,
            name="branch_membership_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        default=MembershipStatus.ACTIVE,
        nullable=False,
    )
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
