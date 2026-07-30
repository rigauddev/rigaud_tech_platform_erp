import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.infrastructure.repositories import SQLAlchemyAuthSessionRepository
from app.modules.auth.presentation.dependencies import get_current_user, get_password_service
from app.modules.companies.application.use_cases import EnsureDefaultMembershipForUser
from app.modules.companies.domain.exceptions import CompanyNotFoundError
from app.modules.companies.infrastructure.repositories import (
    SQLAlchemyBranchRepository,
    SQLAlchemyCompanyRepository,
    SQLAlchemyMembershipRepository,
)
from app.modules.users.application.use_cases import (
    ChangeOwnPassword,
    ChangeUserStatus,
    CreateUser,
    GetUser,
    ListUsers,
    ProfileUpdateInput,
    ResetUserPassword,
    UpdateOwnProfile,
    UpdateUser,
    UserCreateInput,
    UserListInput,
    UserUpdateInput,
)
from app.modules.users.domain.entities import UserStatus
from app.modules.users.domain.exceptions import (
    InvalidPasswordError,
    InvalidUserDataError,
    UserAlreadyExistsError,
    UserError,
    UserNotFoundError,
    UserPermissionError,
)
from app.modules.users.infrastructure.repositories import SQLAlchemyUserRepository
from app.modules.users.presentation.schemas import (
    ChangePasswordRequest,
    PasswordChangedResponse,
    ResetPasswordRequest,
    UserCreateRequest,
    UserListResponse,
    UserProfileUpdateRequest,
    UserResponse,
    UserUpdateRequest,
)
from app.shared.api.responses import PaginationMeta, error_response, success_response

router = APIRouter(prefix="/users", tags=["Users"])
audit_logger = logging.getLogger("audit")

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]
PasswordServiceDependency = Annotated[PasswordService, Depends(get_password_service)]
PageQuery = Annotated[int, Query(ge=1)]
PageSizeQuery = Annotated[int, Query(ge=1, le=100)]
CompanyQuery = Annotated[UUID | None, Query(alias="company_id")]
StatusQuery = Annotated[UserStatus | None, Query(alias="status")]
SearchQuery = Annotated[str | None, Query(max_length=120)]


def _user_response(user) -> UserResponse:
    return UserResponse(
        id=user.id,
        tenant_id=user.tenant_id,
        tenant_slug=user.tenant_slug,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        display_name=user.display_name,
        phone=user.phone,
        status=user.status,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        must_change_password=user.must_change_password,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


def _require_superuser(current_user: AuthenticatedUser) -> JSONResponse | None:
    if current_user.is_superuser:
        return None
    return error_response("AUTH_FORBIDDEN")


def _request_id(request: Request) -> str | None:
    return request.headers.get("x-request-id")


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    password_service: PasswordServiceDependency,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        user = await CreateUser(
            SQLAlchemyUserRepository(session),
            SQLAlchemyCompanyRepository(session),
            password_service,
        ).execute(
            UserCreateInput(
                tenant_id=payload.tenant_id,
                email=payload.email,
                password=payload.password,
                first_name=payload.first_name,
                last_name=payload.last_name,
                display_name=payload.display_name,
                phone=payload.phone,
                must_change_password=payload.must_change_password,
                actor_id=current_user.id,
            )
        )
        audit_logger.info(
            "user.created",
            extra={
                "event": "user.created",
                "actor_id": str(current_user.id),
                "user_id": str(user.id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="user.created",
                module="users",
                action="created",
                entity_type="user",
                entity_id=user.id,
                tenant_id=user.tenant_id,
                actor_user_id=current_user.id,
                after_data={"id": str(user.id), "email": user.email, "phone": user.phone},
            )
        )
        await EnsureDefaultMembershipForUser(
            SQLAlchemyMembershipRepository(session),
            SQLAlchemyBranchRepository(session),
        ).execute(
            user_id=user.id,
            tenant_id=user.tenant_id,
            is_company_admin=user.is_superuser,
            actor_id=current_user.id,
        )
        await session.commit()
        return success_response("USER_CREATED", data=_user_response(user).model_dump(mode="json"))
    except (UserError, CompanyNotFoundError) as exc:
        await session.rollback()
        return user_exception_to_response(exc)


@router.get("", response_model=UserListResponse)
async def list_users(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    page: PageQuery = 1,
    page_size: PageSizeQuery = 20,
    company_id: CompanyQuery = None,
    status_filter: StatusQuery = None,
    search: SearchQuery = None,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    result = await ListUsers(SQLAlchemyUserRepository(session)).execute(
        UserListInput(
            page=page,
            page_size=page_size,
            tenant_id=company_id,
            status=status_filter,
            search=search,
        )
    )
    return success_response(
        "API_SUCCESS",
        data=[_user_response(user).model_dump(mode="json") for user in result.items],
        meta=PaginationMeta.from_total(
            page=result.page,
            page_size=result.page_size,
            total=result.total,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_my_user(
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        user = await GetUser(SQLAlchemyUserRepository(session)).execute(
            current_user.id,
            actor_id=current_user.id,
            actor_is_superuser=False,
        )
        return success_response("API_SUCCESS", data=_user_response(user).model_dump(mode="json"))
    except UserError as exc:
        return user_exception_to_response(exc)


@router.patch("/me", response_model=UserResponse)
async def update_my_profile(
    payload: UserProfileUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        user = await UpdateOwnProfile(SQLAlchemyUserRepository(session)).execute(
            current_user.id,
            ProfileUpdateInput(
                first_name=payload.first_name,
                last_name=payload.last_name,
                display_name=payload.display_name,
                phone=payload.phone,
                actor_id=current_user.id,
            ),
        )
        audit_logger.info(
            "user.profile_updated",
            extra={
                "event": "user.profile_updated",
                "actor_id": str(current_user.id),
                "user_id": str(user.id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="user.profile_updated",
                module="users",
                action="profile_updated",
                entity_type="user",
                entity_id=user.id,
                tenant_id=user.tenant_id,
                actor_user_id=current_user.id,
                after_data={"id": str(user.id), "email": user.email, "phone": user.phone},
            )
        )
        await session.commit()
        return success_response("USER_UPDATED", data=_user_response(user).model_dump(mode="json"))
    except UserError as exc:
        await session.rollback()
        return user_exception_to_response(exc)


@router.post("/me/change-password", response_model=PasswordChangedResponse)
async def change_my_password(
    payload: ChangePasswordRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    password_service: PasswordServiceDependency,
) -> JSONResponse:
    try:
        await ChangeOwnPassword(
            SQLAlchemyUserRepository(session),
            SQLAlchemyAuthSessionRepository(session),
            password_service,
        ).execute(current_user.id, payload.current_password, payload.new_password)
        audit_logger.info(
            "user.password_changed",
            extra={
                "event": "user.password.changed",
                "actor_id": str(current_user.id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="user.password.changed",
                module="users",
                action="password_changed",
                entity_type="user",
                entity_id=current_user.id,
                tenant_id=current_user.tenant_id,
                actor_user_id=current_user.id,
            )
        )
        await session.commit()
        return success_response(
            "USER_PASSWORD_CHANGED",
            data=PasswordChangedResponse(
                message="Senha alterada. Faça login novamente."
            ).model_dump(),
        )
    except UserError as exc:
        await session.rollback()
        return user_exception_to_response(exc)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    try:
        user = await GetUser(SQLAlchemyUserRepository(session)).execute(
            user_id,
            actor_id=current_user.id,
            actor_is_superuser=current_user.is_superuser,
        )
        return success_response("API_SUCCESS", data=_user_response(user).model_dump(mode="json"))
    except UserError as exc:
        return user_exception_to_response(exc)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    payload: UserUpdateRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        user = await UpdateUser(SQLAlchemyUserRepository(session)).execute(
            user_id,
            UserUpdateInput(
                email=payload.email,
                first_name=payload.first_name,
                last_name=payload.last_name,
                display_name=payload.display_name,
                phone=payload.phone,
                status=payload.status,
                must_change_password=payload.must_change_password,
                actor_id=current_user.id,
            ),
        )
        audit_logger.info(
            "user.updated",
            extra={
                "event": "user.updated",
                "actor_id": str(current_user.id),
                "user_id": str(user.id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="user.updated",
                module="users",
                action="updated",
                entity_type="user",
                entity_id=user.id,
                tenant_id=user.tenant_id,
                actor_user_id=current_user.id,
                after_data={"id": str(user.id), "email": user.email, "status": user.status},
            )
        )
        await session.commit()
        return success_response("USER_UPDATED", data=_user_response(user).model_dump(mode="json"))
    except UserError as exc:
        await session.rollback()
        return user_exception_to_response(exc)


@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        user_id, UserStatus.ACTIVE, "user.activated", request, session, current_user
    )


@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        user_id, UserStatus.INACTIVE, "user.deactivated", request, session, current_user
    )


@router.post("/{user_id}/block", response_model=UserResponse)
async def block_user(
    user_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        user_id, UserStatus.BLOCKED, "user.blocked", request, session, current_user
    )


@router.post("/{user_id}/unblock", response_model=UserResponse)
async def unblock_user(
    user_id: UUID,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
) -> JSONResponse:
    return await _change_status(
        user_id, UserStatus.ACTIVE, "user.unblocked", request, session, current_user
    )


@router.post("/{user_id}/reset-password", response_model=PasswordChangedResponse)
async def reset_user_password(
    user_id: UUID,
    payload: ResetPasswordRequest,
    request: Request,
    session: AsyncSessionDependency,
    current_user: CurrentUserDependency,
    password_service: PasswordServiceDependency,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        await ResetUserPassword(
            SQLAlchemyUserRepository(session),
            SQLAlchemyAuthSessionRepository(session),
            password_service,
        ).execute(user_id, payload.temporary_password, actor_id=current_user.id)
        audit_logger.info(
            "user.password_reset",
            extra={
                "event": "user.password.reset",
                "actor_id": str(current_user.id),
                "user_id": str(user_id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="user.password.reset",
                module="users",
                action="password_reset",
                entity_type="user",
                entity_id=user_id,
                actor_user_id=current_user.id,
            )
        )
        await session.commit()
        return success_response(
            "USER_PASSWORD_RESET",
            data=PasswordChangedResponse(
                message="Senha temporária definida. Usuário deve trocar a senha."
            ).model_dump(),
        )
    except UserError as exc:
        await session.rollback()
        return user_exception_to_response(exc)


async def _change_status(
    user_id: UUID,
    new_status: UserStatus,
    event: str,
    request: Request,
    session: AsyncSession,
    current_user: AuthenticatedUser,
) -> JSONResponse:
    if error := _require_superuser(current_user):
        return error
    try:
        user = await ChangeUserStatus(
            SQLAlchemyUserRepository(session),
            SQLAlchemyAuthSessionRepository(session),
        ).execute(user_id, new_status, actor_id=current_user.id)
        audit_logger.info(
            event,
            extra={
                "event": event,
                "actor_id": str(current_user.id),
                "user_id": str(user.id),
                "request_id": _request_id(request),
            },
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name=event,
                module="users",
                action=event.split(".")[-1],
                entity_type="user",
                entity_id=user.id,
                tenant_id=user.tenant_id,
                actor_user_id=current_user.id,
                after_data={"id": str(user.id), "status": user.status},
            )
        )
        await session.commit()
        return success_response("USER_UPDATED", data=_user_response(user).model_dump(mode="json"))
    except UserError as exc:
        await session.rollback()
        return user_exception_to_response(exc)


def user_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, (UserNotFoundError, CompanyNotFoundError)):
        return error_response("USER_NOT_FOUND")
    if isinstance(exc, UserPermissionError):
        return error_response("AUTH_FORBIDDEN")
    if isinstance(exc, UserAlreadyExistsError):
        return error_response("USER_EMAIL_ALREADY_EXISTS")
    if isinstance(exc, InvalidPasswordError):
        return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
    if isinstance(exc, InvalidUserDataError):
        return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
    return error_response("VALIDATION_ERROR", status_code=status.HTTP_400_BAD_REQUEST)
