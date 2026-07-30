from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.companies.domain.entities import (
    AccessScope,
    BranchRole,
    BranchStatus,
    BranchType,
    CompanyRole,
    CompanyStatus,
    MembershipStatus,
)


class CompanyBaseSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CompanyCreateRequest(CompanyBaseSchema):
    legal_name: str = Field(min_length=1, max_length=180)
    trade_name: str = Field(min_length=1, max_length=120)
    document: str = Field(min_length=14, max_length=32)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=32)
    slug: str = Field(min_length=1, max_length=80)
    code: str = Field(min_length=2, max_length=20)
    timezone: str | None = Field(default="America/Sao_Paulo", max_length=64)
    locale: str | None = Field(default="pt-BR", max_length=16)
    currency: str | None = Field(default="BRL", max_length=3)


class CompanyUpdateRequest(CompanyBaseSchema):
    legal_name: str | None = Field(default=None, min_length=1, max_length=180)
    trade_name: str | None = Field(default=None, min_length=1, max_length=120)
    document: str | None = Field(default=None, min_length=14, max_length=32)
    email: str | None = Field(default=None, max_length=320)
    phone: str | None = Field(default=None, max_length=32)
    slug: str | None = Field(default=None, min_length=1, max_length=80)
    code: str | None = Field(default=None, min_length=2, max_length=20)
    timezone: str | None = Field(default=None, max_length=64)
    locale: str | None = Field(default=None, max_length=16)
    currency: str | None = Field(default=None, max_length=3)


class CompanyResponse(CompanyBaseSchema):
    id: UUID
    legal_name: str
    trade_name: str
    document: str
    email: str | None
    phone: str | None
    slug: str
    code: str
    status: CompanyStatus
    timezone: str
    locale: str
    currency: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyListResponse(CompanyBaseSchema):
    items: list[CompanyResponse]
    total: int
    page: int
    page_size: int


class BranchCreateRequest(CompanyBaseSchema):
    tenant_id: UUID
    code: str = Field(min_length=2, max_length=40)
    name: str = Field(min_length=1, max_length=120)
    legal_name: str | None = Field(default=None, max_length=180)
    trade_name: str | None = Field(default=None, max_length=120)
    document: str | None = Field(default=None, max_length=32)
    branch_type: BranchType = BranchType.STORE
    is_headquarters: bool = False
    timezone: str | None = Field(default=None, max_length=64)
    phone: str | None = Field(default=None, max_length=32)
    email: str | None = Field(default=None, max_length=320)
    address: str | None = Field(default=None, max_length=500)


class BranchResponse(CompanyBaseSchema):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    legal_name: str | None
    trade_name: str | None
    document: str | None
    branch_type: BranchType
    status: BranchStatus
    is_headquarters: bool
    timezone: str
    phone: str | None
    email: str | None
    address: str | None
    created_at: datetime
    updated_at: datetime


class BranchListResponse(CompanyBaseSchema):
    items: list[BranchResponse]
    total: int
    page: int
    page_size: int


class BranchMembershipResponse(CompanyBaseSchema):
    id: UUID
    branch_id: UUID
    role: BranchRole
    status: MembershipStatus
    is_default: bool


class CompanyMembershipResponse(CompanyBaseSchema):
    id: UUID
    tenant_id: UUID
    role: CompanyRole
    status: MembershipStatus
    access_scope: AccessScope
    is_default: bool
    branches: list[BranchMembershipResponse]


class ActiveContextResponse(CompanyBaseSchema):
    tenant_id: UUID
    membership_id: UUID | None
    branch_id: UUID | None
    branch_membership_id: UUID | None
    role: str | None
    access_scope: AccessScope | None


class ContextOptionsResponse(CompanyBaseSchema):
    active_context: ActiveContextResponse
    memberships: list[CompanyMembershipResponse]
