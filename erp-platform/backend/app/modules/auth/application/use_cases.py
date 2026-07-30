from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from app.core.config import settings
from app.database import set_tenant_id
from app.modules.auth.application.email import normalize_email, normalize_tenant
from app.modules.auth.application.mfa_services import (
    DevelopmentEmailOtpSender,
    DevelopmentSmsOtpSender,
    OtpService,
    RecoveryCodeService,
    TotpService,
)
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.domain.entities import AuthenticatedUser, TokenPair
from app.modules.auth.domain.exceptions import (
    BlockedUserError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidTokenError,
    MfaChallengeExpiredError,
    MfaChallengeLockedError,
    MfaInvalidCodeError,
    MfaMethodNotActiveError,
    MfaMethodNotFoundError,
    RevokedTokenError,
)
from app.modules.auth.domain.mfa import LoginMfaChallenge, LoginMfaMethod, MfaMethodType
from app.modules.auth.domain.repositories import (
    AuthSessionRepository,
    EmailOtpSender,
    MfaChallengeStore,
    MfaMethodRepository,
    MfaRecoveryCodeRepository,
    SmsOtpSender,
    TenantResolver,
    UserAuthRepository,
    to_authenticated_user,
)
from app.modules.auth.infrastructure.models import AuthSessionModel
from app.modules.users.domain.entities import UserStatus


@dataclass(frozen=True)
class LoginInput:
    tenant: str
    email: str
    password: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class RefreshInput:
    refresh_token: str
    user_agent: str | None = None
    ip_address: str | None = None


@dataclass(frozen=True)
class LogoutInput:
    refresh_token: str


class AuthenticateUser:
    def __init__(
        self,
        users: UserAuthRepository,
        sessions: AuthSessionRepository,
        tenants: TenantResolver,
        password_service: PasswordService,
        token_service: TokenService,
        mfa_methods: MfaMethodRepository | None = None,
        mfa_challenges: MfaChallengeStore | None = None,
        otp_service: OtpService | None = None,
        email_sender: EmailOtpSender | None = None,
        sms_sender: SmsOtpSender | None = None,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.tenants = tenants
        self.password_service = password_service
        self.token_service = token_service
        self.mfa_methods = mfa_methods
        self.mfa_challenges = mfa_challenges
        self.otp_service = otp_service or OtpService()
        self.email_sender = email_sender or DevelopmentEmailOtpSender()
        self.sms_sender = sms_sender or DevelopmentSmsOtpSender()

    async def execute(self, input_data: LoginInput) -> TokenPair | LoginMfaChallenge:
        try:
            tenant = normalize_tenant(input_data.tenant)
            email = normalize_email(input_data.email)
        except ValueError as exc:
            raise InvalidCredentialsError("Invalid credentials.") from exc

        tenant_id = await self.tenants.resolve_by_slug_or_code(tenant)
        if tenant_id is None:
            raise InvalidCredentialsError("Invalid credentials.")

        user = await self.users.get_by_email_and_tenant_id(email=email, tenant_id=tenant_id)
        if user is None:
            raise InvalidCredentialsError("Invalid credentials.")
        if not self.password_service.verify(input_data.password, user.password_hash):
            await self.users.increment_failed_login(user)
            raise InvalidCredentialsError("Invalid credentials.")
        now = datetime.now(UTC)
        if user.status == UserStatus.BLOCKED or (
            user.locked_until is not None and user.locked_until > now
        ):
            raise BlockedUserError("Blocked user.")
        if user.status != UserStatus.ACTIVE or not user.is_active:
            raise InactiveUserError("Inactive user.")
        if user.deleted_at is not None:
            raise InvalidCredentialsError("Invalid credentials.")

        if self.mfa_methods is not None and self.mfa_challenges is not None:
            active_methods = await self.mfa_methods.list_active_for_user(user.id, user.tenant_id)
            if active_methods:
                challenge = {
                    "purpose": "login",
                    "user_id": str(user.id),
                    "tenant_id": str(user.tenant_id),
                    "methods": [method.method_type.value for method in active_methods],
                    "attempts": 0,
                    "max_attempts": 5,
                    "ip_address": input_data.ip_address,
                    "user_agent": input_data.user_agent,
                }
                challenge_id = await self.mfa_challenges.create(
                    challenge, settings.mfa_challenge_expire_seconds
                )
                primary = next(
                    (method for method in active_methods if method.is_primary), active_methods[0]
                )
                if primary.method_type in {MfaMethodType.EMAIL, MfaMethodType.SMS}:
                    code = self.otp_service.generate()
                    challenge["otp_hash"] = self.otp_service.hash_code(code, salt=challenge_id)
                    await self.mfa_challenges.update(
                        challenge_id, challenge, settings.mfa_challenge_expire_seconds
                    )
                    if primary.method_type == MfaMethodType.EMAIL:
                        await self.email_sender.send_code(user.email, code)
                    else:
                        await self.sms_sender.send_code(user.phone or "", code)
                return LoginMfaChallenge(
                    challenge_id=challenge_id,
                    available_methods=[
                        LoginMfaMethod(
                            id=method.id,
                            type=method.method_type,
                            destination=method.destination_masked,
                        )
                        for method in active_methods
                    ],
                    expires_in=settings.mfa_challenge_expire_seconds,
                )

        return await self.issue_tokens(
            user=user,
            user_agent=input_data.user_agent,
            ip_address=input_data.ip_address,
            logged_at=now,
        )

    async def issue_tokens(
        self,
        user: Any,
        user_agent: str | None,
        ip_address: str | None,
        logged_at: datetime | None = None,
    ) -> TokenPair:
        return await issue_token_pair(
            user=user,
            sessions=self.sessions,
            users=self.users,
            token_service=self.token_service,
            user_agent=user_agent,
            ip_address=ip_address,
            logged_at=logged_at,
        )


@dataclass(frozen=True)
class VerifyLoginMfaInput:
    challenge_id: str
    method: MfaMethodType
    code: str
    user_agent: str | None = None
    ip_address: str | None = None


class VerifyLoginMfaChallenge:
    def __init__(
        self,
        users: UserAuthRepository,
        sessions: AuthSessionRepository,
        mfa_methods: MfaMethodRepository,
        recovery_codes: MfaRecoveryCodeRepository,
        mfa_challenges: MfaChallengeStore,
        token_service: TokenService,
        totp_service: TotpService,
        otp_service: OtpService,
        recovery_code_service: RecoveryCodeService,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.mfa_methods = mfa_methods
        self.recovery_codes = recovery_codes
        self.mfa_challenges = mfa_challenges
        self.token_service = token_service
        self.totp_service = totp_service
        self.otp_service = otp_service
        self.recovery_code_service = recovery_code_service

    async def execute(self, input_data: VerifyLoginMfaInput) -> TokenPair:
        challenge = await self.mfa_challenges.get(input_data.challenge_id)
        if challenge is None or challenge.get("purpose") != "login":
            raise MfaChallengeExpiredError("MFA challenge expired.")
        attempts = int(challenge.get("attempts", 0))
        max_attempts = int(challenge.get("max_attempts", 5))
        if attempts >= max_attempts:
            raise MfaChallengeLockedError("MFA challenge locked.")

        user_id = UUID(str(challenge["user_id"]))
        tenant_id = UUID(str(challenge["tenant_id"]))
        user = await self.users.get_by_id(user_id)
        if user is None or user.tenant_id != tenant_id or user.deleted_at is not None:
            raise MfaChallengeExpiredError("MFA challenge expired.")

        valid = False
        method = None
        if input_data.method == MfaMethodType.RECOVERY_CODE:
            code_hash = self.recovery_code_service.hash_code(user.id, input_data.code)
            recovery_code = await self.recovery_codes.get_active_by_hash(
                user.id, user.tenant_id, code_hash
            )
            if recovery_code is not None:
                recovery_code.used_at = datetime.now(UTC)
                valid = True
        else:
            if input_data.method.value not in challenge.get("methods", []):
                raise MfaMethodNotActiveError("MFA method is not active.")
            method = await self.mfa_methods.get_by_user_and_type(user.id, input_data.method)
            if method is None:
                raise MfaMethodNotFoundError("MFA method not found.")
            if input_data.method == MfaMethodType.TOTP and method.encrypted_secret:
                valid = self.totp_service.verify(method.encrypted_secret, input_data.code)
            elif input_data.method in {MfaMethodType.EMAIL, MfaMethodType.SMS}:
                expected_hash = str(challenge.get("otp_hash", ""))
                valid = self.otp_service.verify(
                    input_data.code,
                    salt=input_data.challenge_id,
                    expected_hash=expected_hash,
                )

        if not valid:
            challenge["attempts"] = attempts + 1
            await self.mfa_challenges.update(
                input_data.challenge_id,
                challenge,
                settings.mfa_challenge_expire_seconds,
            )
            raise MfaInvalidCodeError("Invalid MFA code.")

        if method is not None:
            method.last_used_at = datetime.now(UTC)
        await self.mfa_challenges.delete(input_data.challenge_id)
        return await issue_token_pair(
            user=user,
            sessions=self.sessions,
            users=self.users,
            token_service=self.token_service,
            user_agent=input_data.user_agent,
            ip_address=input_data.ip_address,
        )


async def issue_token_pair(
    *,
    user: Any,
    sessions: AuthSessionRepository,
    users: UserAuthRepository,
    token_service: TokenService,
    user_agent: str | None,
    ip_address: str | None,
    logged_at: datetime | None = None,
) -> TokenPair:
    refresh_token = token_service.create_refresh_token()
    session = AuthSessionModel(
        user_id=user.id,
        tenant_id=user.tenant_id,
        refresh_token_hash=refresh_token.token_hash,
        expires_at=refresh_token.expires_at,
        user_agent=user_agent,
        ip_address=ip_address,
    )
    await sessions.create(session)
    await users.update_last_login(user, logged_at or datetime.now(UTC))
    set_tenant_id(user.tenant_id)
    return TokenPair(
        access_token=token_service.create_access_token(user.id, user.tenant_id),
        refresh_token=refresh_token.token,
        token_type="bearer",
        expires_in=token_service.access_token_expires_in,
    )


class RefreshSession:
    def __init__(
        self,
        users: UserAuthRepository,
        sessions: AuthSessionRepository,
        token_service: TokenService,
    ) -> None:
        self.users = users
        self.sessions = sessions
        self.token_service = token_service

    async def execute(self, input_data: RefreshInput) -> TokenPair:
        token_hash = self.token_service.hash_refresh_token(input_data.refresh_token)
        session = await self.sessions.get_by_refresh_token_hash(token_hash)
        now = datetime.now(UTC)

        if session is None:
            raise InvalidTokenError("Invalid refresh token.")
        if session.revoked_at is not None:
            await self.sessions.revoke_session_chain(session, now)
            raise RevokedTokenError("Refresh token has been revoked.")
        if session.expires_at <= now:
            await self.sessions.revoke(session, now)
            raise InvalidTokenError("Refresh token expired.")

        user = await self.users.get_by_id(session.user_id)
        if user is None or user.deleted_at is not None:
            raise InvalidTokenError("Invalid refresh token.")
        if user.status == UserStatus.BLOCKED or (
            user.locked_until is not None and user.locked_until > now
        ):
            raise BlockedUserError("Blocked user.")
        if user.status != UserStatus.ACTIVE or not user.is_active:
            raise InactiveUserError("Inactive user.")

        refresh_token = self.token_service.create_refresh_token()
        new_session = AuthSessionModel(
            user_id=user.id,
            tenant_id=user.tenant_id,
            refresh_token_hash=refresh_token.token_hash,
            expires_at=refresh_token.expires_at,
            user_agent=input_data.user_agent,
            ip_address=input_data.ip_address,
        )
        await self.sessions.create(new_session)
        session.revoked_at = now
        session.replaced_by_session_id = new_session.id
        set_tenant_id(user.tenant_id)

        return TokenPair(
            access_token=self.token_service.create_access_token(user.id, user.tenant_id),
            refresh_token=refresh_token.token,
            token_type="bearer",
            expires_in=self.token_service.access_token_expires_in,
        )


class LogoutSession:
    def __init__(self, sessions: AuthSessionRepository, token_service: TokenService) -> None:
        self.sessions = sessions
        self.token_service = token_service

    async def execute(self, input_data: LogoutInput) -> None:
        token_hash = self.token_service.hash_refresh_token(input_data.refresh_token)
        session = await self.sessions.get_by_refresh_token_hash(token_hash)
        if session is None or session.revoked_at is not None:
            return
        await self.sessions.revoke(session, datetime.now(UTC))


class GetCurrentUser:
    def __init__(self, users: UserAuthRepository, token_service: TokenService) -> None:
        self.users = users
        self.token_service = token_service

    async def execute(self, access_token: str) -> AuthenticatedUser:
        payload = self.token_service.decode_access_token(access_token)
        try:
            user_id = UUID(str(payload["sub"]))
            tenant_id = UUID(str(payload["tenant_id"]))
        except (KeyError, ValueError) as exc:
            raise InvalidTokenError("Invalid token.") from exc

        user = await self.users.get_by_id(user_id)
        if user is None or user.tenant_id != tenant_id:
            raise InvalidTokenError("Invalid token.")
        if user.deleted_at is not None:
            raise InvalidTokenError("Invalid token.")
        now = datetime.now(UTC)
        if user.status == UserStatus.BLOCKED or (
            user.locked_until is not None and user.locked_until > now
        ):
            raise BlockedUserError("Blocked user.")
        if user.status != UserStatus.ACTIVE or not user.is_active:
            raise InactiveUserError("Inactive user.")

        set_tenant_id(user.tenant_id)
        return to_authenticated_user(user)
