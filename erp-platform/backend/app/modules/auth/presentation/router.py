import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import clear_tenant_id, get_async_session
from app.modules.audit.application.service import AuditEventInput, AuditService
from app.modules.audit.infrastructure.repositories import SQLAlchemyAuditEventRepository
from app.modules.auth.application.mfa_services import (
    OtpService,
    RecoveryCodeService,
    TotpService,
)
from app.modules.auth.application.mfa_use_cases import (
    BeginOtpEnrollment,
    BeginTotpEnrollment,
    ConfirmOtpEnrollment,
    ConfirmTotpEnrollment,
    DisableMfa,
    DisableMfaMethod,
    GenerateRecoveryCodes,
    GetMfaStatus,
    SetPrimaryMfaMethod,
)
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.application.use_cases import (
    AuthenticateUser,
    LoginInput,
    LogoutInput,
    LogoutSession,
    RefreshInput,
    RefreshSession,
    VerifyLoginMfaChallenge,
    VerifyLoginMfaInput,
)
from app.modules.auth.domain.entities import AuthenticatedUser
from app.modules.auth.domain.exceptions import (
    AuthenticationRequiredError,
    BlockedUserError,
    ExpiredTokenError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    MfaAlreadyEnabledError,
    MfaChallengeExpiredError,
    MfaChallengeLockedError,
    MfaInvalidCodeError,
    MfaMethodNotActiveError,
    MfaMethodNotFoundError,
    MfaNotEnabledError,
    MfaProviderUnavailableError,
    RevokedTokenError,
    TenantInactiveError,
    TenantSuspendedError,
)
from app.modules.auth.domain.mfa import LoginMfaChallenge, MfaMethodType
from app.modules.auth.infrastructure.mfa_challenges import RedisMfaChallengeStore
from app.modules.auth.infrastructure.repositories import (
    SQLAlchemyAuthSessionRepository,
    SQLAlchemyMfaMethodRepository,
    SQLAlchemyMfaRecoveryCodeRepository,
    SQLAlchemyTenantResolver,
    SQLAlchemyUserAuthRepository,
)
from app.modules.auth.presentation.dependencies import (
    get_current_user,
    get_password_service,
    get_token_service,
)
from app.modules.auth.presentation.schemas import (
    CurrentUserResponse,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    MfaCodeRequest,
    MfaDisableRequest,
    MfaLoginMethodResponse,
    MfaMessageResponse,
    MfaOtpConfirmRequest,
    MfaOtpSetupResponse,
    MfaRecoveryCodesResponse,
    MfaRequiredResponse,
    MfaStatusResponse,
    MfaTotpSetupResponse,
    MfaVerifyRequest,
    RefreshRequest,
    TokenResponse,
)
from app.shared.api.responses import error_response, success_response

router = APIRouter(prefix="/auth", tags=["Auth"])
audit_logger = logging.getLogger("audit")
AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]
PasswordServiceDependency = Annotated[PasswordService, Depends(get_password_service)]
TokenServiceDependency = Annotated[TokenService, Depends(get_token_service)]
CurrentUserDependency = Annotated[AuthenticatedUser, Depends(get_current_user)]


def _client_ip(request: Request) -> str | None:
    if request.client is None:
        return None
    return request.client.host


def _user_agent(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent")
    if user_agent is None:
        return None
    return user_agent[:255]


def _audit_service(session: AsyncSession) -> AuditService:
    return AuditService(SQLAlchemyAuditEventRepository(session))


async def _full_current_user(session: AsyncSession, current_user: AuthenticatedUser):
    user = await SQLAlchemyUserAuthRepository(session).get_by_id(current_user.id)
    if user is None:
        raise InvalidTokenError("Invalid token.")
    return user


def _mfa_methods(session: AsyncSession) -> SQLAlchemyMfaMethodRepository:
    return SQLAlchemyMfaMethodRepository(session)


def _mfa_recovery_codes(session: AsyncSession) -> SQLAlchemyMfaRecoveryCodeRepository:
    return SQLAlchemyMfaRecoveryCodeRepository(session)


def _mfa_challenges() -> RedisMfaChallengeStore:
    return RedisMfaChallengeStore()


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    session: AsyncSessionDependency,
    password_service: PasswordServiceDependency,
    token_service: TokenServiceDependency,
) -> JSONResponse:
    use_case = AuthenticateUser(
        users=SQLAlchemyUserAuthRepository(session),
        sessions=SQLAlchemyAuthSessionRepository(session),
        tenants=SQLAlchemyTenantResolver(session),
        password_service=password_service,
        token_service=token_service,
        mfa_methods=_mfa_methods(session),
        mfa_challenges=_mfa_challenges(),
        otp_service=OtpService(),
    )
    try:
        token_pair = await use_case.execute(
            LoginInput(
                tenant=payload.tenant,
                email=payload.email,
                password=payload.password,
                user_agent=_user_agent(request),
                ip_address=_client_ip(request),
            )
        )
        if isinstance(token_pair, LoginMfaChallenge):
            await _audit_service(session).record_event(
                AuditEventInput(
                    event_name="auth.mfa.challenge.created",
                    module="auth",
                    action="mfa_challenge_created",
                    metadata={"tenant": payload.tenant, "email": payload.email},
                    ip_address=_client_ip(request),
                    user_agent=_user_agent(request),
                )
            )
            await session.commit()
            return success_response(
                "AUTH_MFA_REQUIRED",
                data=MfaRequiredResponse(
                    mfa_required=True,
                    challenge_id=token_pair.challenge_id,
                    available_methods=[
                        MfaLoginMethodResponse(
                            id=method.id,
                            type=method.type.value,
                            destination=method.destination,
                        )
                        for method in token_pair.available_methods
                    ],
                    expires_in=token_pair.expires_in,
                ).model_dump(mode="json"),
            )

        await session.commit()
        audit_logger.info(
            "auth.login.success", extra={"event": "auth.login.success", "tenant": payload.tenant}
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="auth.login.success",
                module="auth",
                action="login",
                metadata={"tenant": payload.tenant, "email": payload.email},
                ip_address=_client_ip(request),
                user_agent=_user_agent(request),
            )
        )
        await session.commit()
        return success_response(
            "API_SUCCESS", data=TokenResponse(**token_pair.__dict__).model_dump()
        )
    except InvalidCredentialsError:
        audit_logger.info(
            "auth.login.failed", extra={"event": "auth.login.failed", "tenant": payload.tenant}
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="auth.login.failed",
                module="auth",
                action="login_failed",
                metadata={"tenant": payload.tenant, "email": payload.email},
                ip_address=_client_ip(request),
                user_agent=_user_agent(request),
            )
        )
        await session.commit()
        return error_response("AUTH_INVALID_CREDENTIALS")
    except InactiveUserError:
        await session.rollback()
        audit_logger.info(
            "auth.login.failed", extra={"event": "auth.login.failed", "tenant": payload.tenant}
        )
        return error_response("AUTH_USER_INACTIVE")
    except BlockedUserError:
        audit_logger.info(
            "auth.login.failed", extra={"event": "auth.login.failed", "tenant": payload.tenant}
        )
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="auth.login.blocked",
                module="auth",
                action="login_blocked",
                metadata={"tenant": payload.tenant, "email": payload.email},
                ip_address=_client_ip(request),
                user_agent=_user_agent(request),
            )
        )
        await session.commit()
        return error_response("AUTH_USER_BLOCKED")
    except (TenantInactiveError, TenantSuspendedError):
        await session.rollback()
        audit_logger.info(
            "auth.login.failed", extra={"event": "auth.login.failed", "tenant": payload.tenant}
        )
        return error_response("AUTH_FORBIDDEN")
    finally:
        clear_tenant_id()


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    payload: RefreshRequest,
    request: Request,
    session: AsyncSessionDependency,
    token_service: TokenServiceDependency,
) -> JSONResponse:
    use_case = RefreshSession(
        users=SQLAlchemyUserAuthRepository(session),
        sessions=SQLAlchemyAuthSessionRepository(session),
        token_service=token_service,
    )
    try:
        token_pair = await use_case.execute(
            RefreshInput(
                refresh_token=payload.refresh_token,
                user_agent=_user_agent(request),
                ip_address=_client_ip(request),
            )
        )
        await session.commit()
        audit_logger.info("auth.refresh.success", extra={"event": "auth.refresh.success"})
        return success_response(
            "API_SUCCESS", data=TokenResponse(**token_pair.__dict__).model_dump()
        )
    except RevokedTokenError:
        await _audit_service(session).record_event(
            AuditEventInput(
                event_name="auth.refresh.reuse_detected", module="auth", action="refresh_reuse"
            )
        )
        await session.commit()
        audit_logger.warning(
            "auth.token.reuse_detected", extra={"event": "auth.token.reuse_detected"}
        )
        return error_response("AUTH_TOKEN_INVALID")
    except (InvalidTokenError, ExpiredTokenError):
        await session.rollback()
        audit_logger.info("auth.refresh.failed", extra={"event": "auth.refresh.failed"})
        return error_response("AUTH_TOKEN_INVALID")
    except InactiveUserError:
        await session.rollback()
        audit_logger.info("auth.refresh.failed", extra={"event": "auth.refresh.failed"})
        return error_response("AUTH_USER_INACTIVE")
    except BlockedUserError:
        await session.rollback()
        audit_logger.info("auth.refresh.failed", extra={"event": "auth.refresh.failed"})
        return error_response("AUTH_USER_BLOCKED")
    finally:
        clear_tenant_id()


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    payload: LogoutRequest,
    session: AsyncSessionDependency,
    token_service: TokenServiceDependency,
) -> JSONResponse:
    use_case = LogoutSession(
        sessions=SQLAlchemyAuthSessionRepository(session),
        token_service=token_service,
    )
    await use_case.execute(LogoutInput(refresh_token=payload.refresh_token))
    await _audit_service(session).record_event(
        AuditEventInput(event_name="auth.logout", module="auth", action="logout")
    )
    await session.commit()
    audit_logger.info("auth.logout", extra={"event": "auth.logout"})
    clear_tenant_id()
    return success_response(
        "API_SUCCESS", data=LogoutResponse(message="Sessão encerrada.").model_dump()
    )


@router.get("/me", response_model=CurrentUserResponse)
async def me(
    current_user: CurrentUserDependency,
) -> JSONResponse:
    data = CurrentUserResponse(
        id=current_user.id,
        tenant_id=current_user.tenant_id,
        email=current_user.email,
        is_active=current_user.is_active,
        is_superuser=current_user.is_superuser,
    )
    return success_response("API_SUCCESS", data=data.model_dump(mode="json"))


def _status_to_response(status) -> MfaStatusResponse:
    return MfaStatusResponse(
        state=status.state.value,
        enabled=status.enabled,
        primary_method_id=status.primary_method_id,
        methods=[
            {
                "id": method.id,
                "type": method.type.value,
                "status": method.status.value,
                "is_primary": method.is_primary,
                "destination": method.destination,
                "verified_at": method.verified_at.isoformat() if method.verified_at else None,
                "last_used_at": method.last_used_at.isoformat() if method.last_used_at else None,
            }
            for method in status.methods
        ],
        recovery_codes_remaining=status.recovery_codes_remaining,
    )


@router.get("/mfa/status", response_model=MfaStatusResponse)
async def mfa_status(
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    status = await GetMfaStatus(
        methods=_mfa_methods(session),
        recovery_codes=_mfa_recovery_codes(session),
    ).execute(current_user.id, current_user.tenant_id)
    return success_response(
        "AUTH_MFA_STATUS_RETRIEVED", data=_status_to_response(status).model_dump(mode="json")
    )


@router.post("/mfa/totp/setup", response_model=MfaTotpSetupResponse)
async def mfa_totp_setup(
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await BeginTotpEnrollment(_mfa_methods(session), TotpService()).execute(user)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.setup.started",
            module="auth",
            action="mfa_totp_setup_started",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
            metadata={"method": "totp"},
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_SETUP_STARTED",
        data=MfaTotpSetupResponse(**result.__dict__).model_dump(mode="json"),
    )


@router.post("/mfa/totp/confirm")
async def mfa_totp_confirm(
    payload: MfaCodeRequest,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await ConfirmTotpEnrollment(
        methods=_mfa_methods(session),
        recovery_codes=_mfa_recovery_codes(session),
        sessions=SQLAlchemyAuthSessionRepository(session),
        challenges=_mfa_challenges(),
        totp=TotpService(),
        recovery_service=RecoveryCodeService(),
    ).execute(user, payload.code)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.enabled",
            module="auth",
            action="mfa_totp_enabled",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
            metadata={"method": "totp"},
        )
    )
    await session.commit()
    data = (
        MfaRecoveryCodesResponse(codes=result.codes).model_dump()
        if result
        else MfaMessageResponse(message="Autenticação em dois fatores habilitada.").model_dump()
    )
    return success_response("AUTH_MFA_ENABLED", data=data)


@router.post("/mfa/email/setup", response_model=MfaOtpSetupResponse)
async def mfa_email_setup(
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await BeginOtpEnrollment(
        _mfa_methods(session), _mfa_challenges(), OtpService()
    ).execute(user, MfaMethodType.EMAIL)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.setup.started",
            module="auth",
            action="mfa_email_setup_started",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
            metadata={"method": "email"},
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_CODE_SENT", data=MfaOtpSetupResponse(**result.__dict__).model_dump(mode="json")
    )


@router.post("/mfa/email/confirm")
async def mfa_email_confirm(
    payload: MfaOtpConfirmRequest,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await ConfirmOtpEnrollment(
        _mfa_methods(session),
        _mfa_recovery_codes(session),
        SQLAlchemyAuthSessionRepository(session),
        _mfa_challenges(),
        OtpService(),
        RecoveryCodeService(),
    ).execute(user, MfaMethodType.EMAIL, payload.challenge_id, payload.code)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.method.added",
            module="auth",
            action="mfa_email_enabled",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
            metadata={"method": "email"},
        )
    )
    await session.commit()
    data = (
        MfaRecoveryCodesResponse(codes=result.codes).model_dump()
        if result
        else MfaMessageResponse(message="Método MFA habilitado.").model_dump()
    )
    return success_response("AUTH_MFA_METHOD_ADDED", data=data)


@router.post("/mfa/sms/setup", response_model=MfaOtpSetupResponse)
async def mfa_sms_setup(
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await BeginOtpEnrollment(
        _mfa_methods(session), _mfa_challenges(), OtpService()
    ).execute(user, MfaMethodType.SMS)
    await session.commit()
    return success_response(
        "AUTH_MFA_CODE_SENT", data=MfaOtpSetupResponse(**result.__dict__).model_dump(mode="json")
    )


@router.post("/mfa/sms/confirm")
async def mfa_sms_confirm(
    payload: MfaOtpConfirmRequest,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await ConfirmOtpEnrollment(
        _mfa_methods(session),
        _mfa_recovery_codes(session),
        SQLAlchemyAuthSessionRepository(session),
        _mfa_challenges(),
        OtpService(),
        RecoveryCodeService(),
    ).execute(user, MfaMethodType.SMS, payload.challenge_id, payload.code)
    await session.commit()
    data = (
        MfaRecoveryCodesResponse(codes=result.codes).model_dump()
        if result
        else MfaMessageResponse(message="Método MFA habilitado.").model_dump()
    )
    return success_response("AUTH_MFA_METHOD_ADDED", data=data)


@router.post("/mfa/methods/{method_id}/primary")
async def mfa_set_primary(
    method_id: str,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    await SetPrimaryMfaMethod(_mfa_methods(session)).execute(user, UUID(method_id))
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.primary.changed",
            module="auth",
            action="mfa_primary_changed",
            entity_id=method_id,
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_PRIMARY_METHOD_CHANGED",
        data=MfaMessageResponse(message="Método principal atualizado.").model_dump(),
    )


@router.delete("/mfa/methods/{method_id}")
async def mfa_disable_method(
    method_id: str,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    await DisableMfaMethod(_mfa_methods(session), SQLAlchemyAuthSessionRepository(session)).execute(
        user, UUID(method_id)
    )
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.method.removed",
            module="auth",
            action="mfa_method_removed",
            entity_id=method_id,
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_METHOD_REMOVED",
        data=MfaMessageResponse(message="Método MFA desabilitado.").model_dump(),
    )


@router.post("/mfa/disable")
async def mfa_disable(
    payload: MfaDisableRequest,
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
    password_service: PasswordServiceDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    await DisableMfa(
        _mfa_methods(session),
        _mfa_recovery_codes(session),
        SQLAlchemyAuthSessionRepository(session),
        _mfa_challenges(),
        password_service,
    ).execute(user, payload.current_password)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.disabled",
            module="auth",
            action="mfa_disabled",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_DISABLED",
        data=MfaMessageResponse(message="Autenticação em dois fatores desabilitada.").model_dump(),
    )


@router.post("/mfa/recovery-codes/regenerate", response_model=MfaRecoveryCodesResponse)
async def mfa_recovery_regenerate(
    current_user: CurrentUserDependency,
    session: AsyncSessionDependency,
) -> JSONResponse:
    user = await _full_current_user(session, current_user)
    result = await GenerateRecoveryCodes(
        _mfa_recovery_codes(session), RecoveryCodeService()
    ).execute(user)
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.recovery_codes.regenerated",
            module="auth",
            action="mfa_recovery_codes_regenerated",
            tenant_id=user.tenant_id,
            actor_user_id=user.id,
        )
    )
    await session.commit()
    return success_response(
        "AUTH_MFA_RECOVERY_CODES_GENERATED",
        data=MfaRecoveryCodesResponse(codes=result.codes).model_dump(),
    )


@router.post("/mfa/verify", response_model=TokenResponse)
async def mfa_verify(
    payload: MfaVerifyRequest,
    request: Request,
    session: AsyncSessionDependency,
    token_service: TokenServiceDependency,
) -> JSONResponse:
    token_pair = await VerifyLoginMfaChallenge(
        users=SQLAlchemyUserAuthRepository(session),
        sessions=SQLAlchemyAuthSessionRepository(session),
        mfa_methods=_mfa_methods(session),
        recovery_codes=_mfa_recovery_codes(session),
        mfa_challenges=_mfa_challenges(),
        token_service=token_service,
        totp_service=TotpService(),
        otp_service=OtpService(),
        recovery_code_service=RecoveryCodeService(),
    ).execute(
        VerifyLoginMfaInput(
            challenge_id=payload.challenge_id,
            method=MfaMethodType(payload.method),
            code=payload.code,
            user_agent=_user_agent(request),
            ip_address=_client_ip(request),
        )
    )
    await _audit_service(session).record_event(
        AuditEventInput(
            event_name="auth.mfa.challenge.verified",
            module="auth",
            action="mfa_challenge_verified",
            metadata={"method": payload.method},
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
        )
    )
    await session.commit()
    return success_response("API_SUCCESS", data=TokenResponse(**token_pair.__dict__).model_dump())


def auth_exception_to_response(exc: Exception) -> JSONResponse:
    if isinstance(exc, MfaAlreadyEnabledError):
        return error_response("AUTH_MFA_ALREADY_ENABLED")
    if isinstance(exc, MfaNotEnabledError):
        return error_response("AUTH_MFA_NOT_ENABLED")
    if isinstance(exc, MfaInvalidCodeError):
        return error_response("AUTH_MFA_CODE_INVALID")
    if isinstance(exc, MfaChallengeExpiredError):
        return error_response("AUTH_MFA_CHALLENGE_EXPIRED")
    if isinstance(exc, MfaChallengeLockedError):
        return error_response("AUTH_MFA_CHALLENGE_LOCKED")
    if isinstance(exc, MfaMethodNotFoundError):
        return error_response("AUTH_MFA_METHOD_NOT_FOUND")
    if isinstance(exc, MfaMethodNotActiveError):
        return error_response("AUTH_MFA_METHOD_NOT_ACTIVE")
    if isinstance(exc, MfaProviderUnavailableError):
        return error_response("AUTH_MFA_PROVIDER_UNAVAILABLE")
    if isinstance(exc, BlockedUserError):
        return error_response("AUTH_USER_BLOCKED")
    if isinstance(exc, InactiveUserError):
        return error_response("AUTH_USER_INACTIVE")
    if isinstance(exc, (AuthenticationRequiredError, InvalidTokenError, ExpiredTokenError)):
        return error_response("AUTH_TOKEN_INVALID")
    return error_response("AUTH_INVALID_CREDENTIALS")
