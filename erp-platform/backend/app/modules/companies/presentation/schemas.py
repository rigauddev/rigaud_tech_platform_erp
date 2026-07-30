from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.companies.domain.entities import CompanyStatus


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
