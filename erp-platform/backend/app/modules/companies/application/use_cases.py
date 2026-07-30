from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError

from app.modules.companies.application.validators import (
    normalize_code,
    normalize_currency,
    normalize_document,
    normalize_email,
    normalize_locale,
    normalize_phone,
    normalize_slug,
    normalize_text,
    normalize_timezone,
)
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.domain.exceptions import (
    CompanyAlreadyExistsError,
    CompanyNotFoundError,
    CompanyPermissionError,
)
from app.modules.companies.domain.repositories import CompanyRepository
from app.modules.companies.infrastructure.models import CompanyModel


@dataclass(frozen=True)
class CompanyCreateInput:
    legal_name: str
    trade_name: str
    document: str
    email: str | None
    phone: str | None
    slug: str
    code: str
    timezone: str | None = None
    locale: str | None = None
    currency: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class CompanyUpdateInput:
    legal_name: str | None = None
    trade_name: str | None = None
    document: str | None = None
    email: str | None = None
    phone: str | None = None
    slug: str | None = None
    code: str | None = None
    timezone: str | None = None
    locale: str | None = None
    currency: str | None = None
    actor_id: UUID | None = None


@dataclass(frozen=True)
class CompanyListInput:
    page: int = 1
    page_size: int = 20
    status: CompanyStatus | None = None
    is_active: bool | None = None
    search: str | None = None


@dataclass(frozen=True)
class CompanyListResult:
    items: list[CompanyModel]
    total: int
    page: int
    page_size: int


class CreateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(self, input_data: CompanyCreateInput) -> CompanyModel:
        legal_name = normalize_text(input_data.legal_name, "legal_name", max_length=180)
        trade_name = normalize_text(input_data.trade_name, "trade_name", max_length=120)
        document = normalize_document(input_data.document)
        slug = normalize_slug(input_data.slug)
        code = normalize_code(input_data.code)
        await self._ensure_unique(document=document, slug=slug, code=code)

        company = CompanyModel(
            legal_name=legal_name,
            trade_name=trade_name,
            document=document,
            email=normalize_email(input_data.email),
            phone=normalize_phone(input_data.phone),
            slug=slug,
            code=code,
            status=CompanyStatus.ACTIVE,
            timezone=normalize_timezone(input_data.timezone),
            locale=normalize_locale(input_data.locale),
            currency=normalize_currency(input_data.currency),
            is_active=True,
            created_by=input_data.actor_id,
            updated_by=input_data.actor_id,
        )
        try:
            return await self.companies.add(company)
        except IntegrityError as exc:
            raise CompanyAlreadyExistsError("Company already exists.") from exc

    async def _ensure_unique(self, *, document: str, slug: str, code: str) -> None:
        if await self.companies.exists_by_document(document):
            raise CompanyAlreadyExistsError("Document already exists.")
        if await self.companies.exists_by_slug(slug):
            raise CompanyAlreadyExistsError("Slug already exists.")
        if await self.companies.exists_by_code(code):
            raise CompanyAlreadyExistsError("Code already exists.")


class GetCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(self, company_id: UUID) -> CompanyModel:
        company = await self.companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        return company


class GetCompanyBySlug:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(self, slug: str) -> CompanyModel:
        company = await self.companies.get_by_slug(normalize_slug(slug))
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        return company


class ListCompanies:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(self, input_data: CompanyListInput) -> CompanyListResult:
        page = max(input_data.page, 1)
        page_size = min(max(input_data.page_size, 1), 100)
        offset = (page - 1) * page_size
        search = input_data.search.strip() if input_data.search else None
        items = await self.companies.list(
            limit=page_size,
            offset=offset,
            status=input_data.status,
            is_active=input_data.is_active,
            search=search,
        )
        total = await self.companies.count(
            status=input_data.status,
            is_active=input_data.is_active,
            search=search,
        )
        return CompanyListResult(items=items, total=total, page=page, page_size=page_size)


class UpdateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(self, company_id: UUID, input_data: CompanyUpdateInput) -> CompanyModel:
        company = await self.companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")

        if input_data.legal_name is not None:
            company.legal_name = normalize_text(input_data.legal_name, "legal_name", max_length=180)
        if input_data.trade_name is not None:
            company.trade_name = normalize_text(input_data.trade_name, "trade_name", max_length=120)
        if input_data.document is not None:
            document = normalize_document(input_data.document)
            if await self.companies.exists_by_document(document, exclude_id=company.id):
                raise CompanyAlreadyExistsError("Document already exists.")
            company.document = document
        if input_data.slug is not None:
            slug = normalize_slug(input_data.slug)
            if await self.companies.exists_by_slug(slug, exclude_id=company.id):
                raise CompanyAlreadyExistsError("Slug already exists.")
            company.slug = slug
        if input_data.code is not None:
            code = normalize_code(input_data.code)
            if await self.companies.exists_by_code(code, exclude_id=company.id):
                raise CompanyAlreadyExistsError("Code already exists.")
            company.code = code
        if input_data.email is not None:
            company.email = normalize_email(input_data.email)
        if input_data.phone is not None:
            company.phone = normalize_phone(input_data.phone)
        if input_data.timezone is not None:
            company.timezone = normalize_timezone(input_data.timezone)
        if input_data.locale is not None:
            company.locale = normalize_locale(input_data.locale)
        if input_data.currency is not None:
            company.currency = normalize_currency(input_data.currency)

        company.updated_by = input_data.actor_id
        try:
            return await self.companies.add(company)
        except IntegrityError as exc:
            raise CompanyAlreadyExistsError("Company already exists.") from exc


class ChangeCompanyStatus:
    def __init__(self, companies: CompanyRepository) -> None:
        self.companies = companies

    async def execute(
        self,
        company_id: UUID,
        status: CompanyStatus,
        *,
        actor_id: UUID | None = None,
    ) -> CompanyModel:
        company = await self.companies.get_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError("Company not found.")
        if status == CompanyStatus.ACTIVE:
            company.activate()
        elif status == CompanyStatus.INACTIVE:
            company.deactivate()
        elif status == CompanyStatus.SUSPENDED:
            company.suspend()
        company.updated_by = actor_id
        return await self.companies.add(company)


class ActivateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.status_changer = ChangeCompanyStatus(companies)

    async def execute(self, company_id: UUID, *, actor_id: UUID | None = None) -> CompanyModel:
        return await self.status_changer.execute(
            company_id,
            CompanyStatus.ACTIVE,
            actor_id=actor_id,
        )


class DeactivateCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.status_changer = ChangeCompanyStatus(companies)

    async def execute(self, company_id: UUID, *, actor_id: UUID | None = None) -> CompanyModel:
        return await self.status_changer.execute(
            company_id,
            CompanyStatus.INACTIVE,
            actor_id=actor_id,
        )


class SuspendCompany:
    def __init__(self, companies: CompanyRepository) -> None:
        self.status_changer = ChangeCompanyStatus(companies)

    async def execute(self, company_id: UUID, *, actor_id: UUID | None = None) -> CompanyModel:
        return await self.status_changer.execute(
            company_id,
            CompanyStatus.SUSPENDED,
            actor_id=actor_id,
        )


class EnsureCompanyAccess:
    def execute(self, *, is_superuser: bool, current_tenant_id: UUID, company_id: UUID) -> None:
        if is_superuser:
            return
        if current_tenant_id == company_id:
            return
        raise CompanyPermissionError("Permission denied.")
