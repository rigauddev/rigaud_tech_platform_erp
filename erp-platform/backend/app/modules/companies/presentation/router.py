import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.companies.application.use_cases import (
    ChangeCompanyStatus,
    CompanyCreateInput,
    CompanyListInput,
    CompanyUpdateInput,
    CreateCompany,
    EnsureCompanyAccess,
    GetCompany,
    ListCompanies,
    UpdateCompany,
)
from app.modules.companies.domain.entities import CompanyStatus
from app.modules.companies.domain.exceptions import (
    CompanyAlreadyExistsError,
    CompanyError,
    CompanyNotFoundError,
    CompanyPermissionError,
    InvalidCompanyDataError,
)
from app.modules.companies.infrastructure.models import CompanyModel
from app.modules.companies.infrastructure.repositories import SQLAlchemyCompanyRepository
from app.modules.companies.presentation.schemas import (
    CompanyCreateRequest,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/companies", tags=["Companies"])
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
StatusQuery = Annotated[CompanyStatus | None, Query(alias="status")]
IsActiveQuery = Annotated[bool | None, Query()]
SearchQuery = Annotated[str | None, Query(max_length=120)]


def _company_response(company: CompanyModel) -> CompanyResponse:
    return CompanyResponse(
        id=company.id,
        legal_name=company.legal_name,
        trade_name=company.trade_name,
        document=company.document,
        email=company.email,
        phone=company.phone,
        slug=company.slug,
        code=company.code,
        status=company.status,
        timezone=company.timezone,
        locale=company.locale,
        currency=company.currency,
        is_active=company.is_active,
        created_at=company.created_at,
        updated_at=company.updated_at,
    )


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


def _require_superuser(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _client_request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    payload: CompanyCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        company = await CreateCompany(SQLAlchemyCompanyRepository(session)).execute(
            CompanyCreateInput(
                legal_name=payload.legal_name,
                trade_name=payload.trade_name,
                document=payload.document,
                email=payload.email,
                phone=payload.phone,
                slug=payload.slug,
                code=payload.code,
                timezone=payload.timezone,
                locale=payload.locale,
                currency=payload.currency,
                actor_id=current_user.id,
            )
        )
        audit_logger.info(
            "company.created",
            extra={
                "event": "company.created",
                "actor_id": str(current_user.id),
                "company_id": str(company.id),
                "request_id": _client_request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="company.created",
                module="companies",
                action="created",
                entity_type="company",
                entity_id=company.id,
                tenant_id=company.id,
                actor_user_id=current_user.id,
                after_data={
                    "id": str(company.id),
                    "document": company.document,
                    "email": company.email,
                },
            )
        )
        await session.commit()
        return success_response(
            "COMPANY_CREATED", data=_company_response(company).model_dump(mode="json")
        )
    except CompanyError as exc:
        await session.rollback()
        return company_exception_to_response(exc)


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    status_filter: StatusQuery = None,
    is_active: IsActiveQuery = None,
    search: SearchQuery = None,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    result = await ListCompanies(SQLAlchemyCompanyRepository(session)).execute(
        CompanyListInput(
            page=page,
            page_size=page_size,
            status=status_filter,
            is_active=is_active,
            search=search,
        )
    )
    return success_response(
        "API_SUCCESS",
        data=[_company_response(company).model_dump(mode="json") for company in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/current", response_model=CompanyResponse)
async def get_current_company(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        company = await GetCompany(SQLAlchemyCompanyRepository(session)).execute(
            current_user.tenant_id
        )
        return success_response(
            "API_SUCCESS", data=_company_response(company).model_dump(mode="json")
        )
    except CompanyError as exc:
        return company_exception_to_response(exc)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        EnsureCompanyAccess().execute(
            is_superuser=current_user.is_superuser,
            current_tenant_id=current_user.tenant_id,
            company_id=company_id,
        )
        company = await GetCompany(SQLAlchemyCompanyRepository(session)).execute(company_id)
        return success_response(
            "API_SUCCESS", data=_company_response(company).model_dump(mode="json")
        )
    except CompanyError as exc:
        return company_exception_to_response(exc)


@router.patch("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: UUID,
    payload: CompanyUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        company = await UpdateCompany(SQLAlchemyCompanyRepository(session)).execute(
            company_id,
            CompanyUpdateInput(
                legal_name=payload.legal_name,
                trade_name=payload.trade_name,
                document=payload.document,
                email=payload.email,
                phone=payload.phone,
                slug=payload.slug,
                code=payload.code,
                timezone=payload.timezone,
                locale=payload.locale,
                currency=payload.currency,
                actor_id=current_user.id,
            ),
        )
        audit_logger.info(
            "company.updated",
            extra={
                "event": "company.updated",
                "actor_id": str(current_user.id),
                "company_id": str(company.id),
                "request_id": _client_request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="company.updated",
                module="companies",
                action="updated",
                entity_type="company",
                entity_id=company.id,
                tenant_id=company.id,
                actor_user_id=current_user.id,
                after_data={
                    "id": str(company.id),
                    "document": company.document,
                    "email": company.email,
                },
            )
        )
        await session.commit()
        return success_response(
            "COMPANY_UPDATED", data=_company_response(company).model_dump(mode="json")
        )
    except CompanyError as exc:
        await session.rollback()
        return company_exception_to_response(exc)


@router.post("/{company_id}/activate", response_model=CompanyResponse)
async def activate_company(
    company_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        company_id,
        CompanyStatus.ACTIVE,
        "company.activated",
        request,
        session,
        current_user,
    )


@router.post("/{company_id}/deactivate", response_model=CompanyResponse)
async def deactivate_company(
    company_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        company_id,
        CompanyStatus.INACTIVE,
        "company.deactivated",
        request,
        session,
        current_user,
    )


@router.post("/{company_id}/suspend", response_model=CompanyResponse)
async def suspend_company(
    company_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        company_id,
        CompanyStatus.SUSPENDED,
        "company.suspended",
        request,
        session,
        current_user,
    )


async def _change_status(
    company_id: UUID,
    next_status: CompanyStatus,
    event_name: str,
    request: Request,
    session: AsyncSession,
    current_user: AuthenticatedUser,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        company = await ChangeCompanyStatus(SQLAlchemyCompanyRepository(session)).execute(
            company_id,
            next_status,
            actor_id=current_user.id,
        )
        audit_logger.info(
            event_name,
            extra={
                "event": event_name,
                "actor_id": str(current_user.id),
                "company_id": str(company.id),
                "request_id": _client_request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name=event_name,
                module="companies",
                action=event_name.split(".")[-1],
                entity_type="company",
                entity_id=company.id,
                tenant_id=company.id,
                actor_user_id=current_user.id,
                after_data={"id": str(company.id), "status": company.status},
            )
        )
        await session.commit()
        return success_response(
            "COMPANY_UPDATED", data=_company_response(company).model_dump(mode="json")
        )
    except CompanyError as exc:
        await session.rollback()
        return company_exception_to_response(exc)


def company_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, CompanyNotFoundError):
        return error_response("COMPANY_NOT_FOUND")
    if isinstance(exc, CompanyAlreadyExistsError):
        return error_response("COMPANY_ALREADY_EXISTS")
    if isinstance(exc, InvalidCompanyDataError):
        return error_response("VALIDATION_ERROR")
    if isinstance(exc, CompanyPermissionError):
        return error_response("AUTH_FORBIDDEN")
    return error_response("VALIDATION_ERROR")
