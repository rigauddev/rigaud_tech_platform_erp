from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.core.config import settings
from app.modules.auth.application.mfa_services import (
    DevelopmentEmailOtpSender,
    DevelopmentSmsOtpSender,
    OtpService,
    RecoveryCodeService,
    TotpEnrollment,
    TotpService,
    mask_email,
    mask_phone,
    utc_now,
)
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.domain.exceptions import (
    MfaAlreadyEnabledError,
    MfaChallengeExpiredError,
    MfaInvalidCodeError,
    MfaMethodNotActiveError,
    MfaMethodNotFoundError,
    MfaNotEnabledError,
)
from app.modules.auth.domain.mfa import (
    MfaMethodStatus,
    MfaMethodSummary,
    MfaMethodType,
    MfaState,
    MfaStatus,
)
from app.modules.auth.domain.repositories import (
    AuthSessionRepository,
    EmailOtpSender,
    MfaChallengeStore,
    MfaMethodRepository,
    MfaRecoveryCodeRepository,
    SmsOtpSender,
)
from app.modules.auth.infrastructure.models import MfaRecoveryCodeModel, UserMfaMethodModel


@dataclass(frozen=True)
class TotpSetupResult:
    method_id: UUID
    secret: str
    otpauth_uri: str
    issuer: str
    expires_in: int


@dataclass(frozen=True)
class OtpSetupResult:
    method_id: UUID
    challenge_id: str
    destination: str | None
    expires_in: int


@dataclass(frozen=True)
class RecoveryCodesResult:
    codes: list[str]


class GetMfaStatus:
    def __init__(
        self,
        methods: MfaMethodRepository,
        recovery_codes: MfaRecoveryCodeRepository,
    ) -> None:
        self.methods = methods
        self.recovery_codes = recovery_codes

    async def execute(self, user_id: UUID, tenant_id: UUID) -> MfaStatus:
        methods = await self.methods.list_for_user(user_id, tenant_id)
        active = [method for method in methods if method.status == MfaMethodStatus.ACTIVE]
        pending = [method for method in methods if method.status == MfaMethodStatus.PENDING]
        recovery = await self.recovery_codes.list_active_for_user(user_id, tenant_id)
        state = MfaState.DISABLED
        if active and not recovery:
            state = MfaState.RECOVERY_REQUIRED
        elif active:
            state = MfaState.ENABLED
        elif pending:
            state = MfaState.PENDING_ENROLLMENT
        primary = next((method.id for method in active if method.is_primary), None)
        return MfaStatus(
            state=state,
            enabled=bool(active),
            primary_method_id=primary,
            methods=[
                MfaMethodSummary(
                    id=method.id,
                    type=method.method_type,
                    status=method.status,
                    is_primary=method.is_primary,
                    destination=method.destination_masked,
                    verified_at=method.verified_at,
                    last_used_at=method.last_used_at,
                )
                for method in methods
            ],
            recovery_codes_remaining=len(recovery),
        )


class BeginTotpEnrollment:
    def __init__(self, methods: MfaMethodRepository, totp: TotpService) -> None:
        self.methods = methods
        self.totp = totp

    async def execute(self, user: object) -> TotpSetupResult:
        existing = await self.methods.get_by_user_and_type(user.id, MfaMethodType.TOTP)
        if existing and existing.status == MfaMethodStatus.ACTIVE:
            raise MfaAlreadyEnabledError("TOTP already enabled.")
        enrollment: TotpEnrollment = self.totp.begin_enrollment(user.email)
        method = existing or UserMfaMethodModel(
            user_id=user.id,
            tenant_id=user.tenant_id,
            method_type=MfaMethodType.TOTP,
        )
        method.status = MfaMethodStatus.PENDING
        method.encrypted_secret = enrollment.encrypted_secret
        method.destination_masked = None
        method.disabled_at = None
        method.is_primary = False
        await self.methods.save(method)
        return TotpSetupResult(
            method_id=method.id,
            secret=enrollment.secret,
            otpauth_uri=enrollment.provisioning_uri,
            issuer=enrollment.issuer,
            expires_in=settings.mfa_challenge_expire_seconds,
        )


class ConfirmTotpEnrollment:
    def __init__(
        self,
        methods: MfaMethodRepository,
        recovery_codes: MfaRecoveryCodeRepository,
        sessions: AuthSessionRepository,
        challenges: MfaChallengeStore,
        totp: TotpService,
        recovery_service: RecoveryCodeService,
    ) -> None:
        self.methods = methods
        self.recovery_codes = recovery_codes
        self.sessions = sessions
        self.challenges = challenges
        self.totp = totp
        self.recovery_service = recovery_service

    async def execute(self, user: object, code: str) -> RecoveryCodesResult | None:
        method = await self.methods.get_by_user_and_type(user.id, MfaMethodType.TOTP)
        if method is None:
            raise MfaMethodNotFoundError("TOTP setup not found.")
        if not method.encrypted_secret or not self.totp.verify(method.encrypted_secret, code):
            raise MfaInvalidCodeError("Invalid TOTP code.")
        active_methods = await self.methods.list_active_for_user(user.id, user.tenant_id)
        if not active_methods:
            await self.methods.unset_primary_for_user(user.id)
            method.is_primary = True
        method.status = MfaMethodStatus.ACTIVE
        method.verified_at = utc_now()
        method.disabled_at = None
        await self.methods.save(method)
        await self.sessions.revoke_all_for_user(user.id, utc_now())
        await self.challenges.revoke_user_challenges(user.id)
        if not await self.recovery_codes.list_active_for_user(user.id, user.tenant_id):
            return await GenerateRecoveryCodes(self.recovery_codes, self.recovery_service).execute(
                user
            )
        return None


class BeginOtpEnrollment:
    def __init__(
        self,
        methods: MfaMethodRepository,
        challenges: MfaChallengeStore,
        otp: OtpService,
        email_sender: EmailOtpSender | None = None,
        sms_sender: SmsOtpSender | None = None,
    ) -> None:
        self.methods = methods
        self.challenges = challenges
        self.otp = otp
        self.email_sender = email_sender or DevelopmentEmailOtpSender()
        self.sms_sender = sms_sender or DevelopmentSmsOtpSender()

    async def execute(self, user: object, method_type: MfaMethodType) -> OtpSetupResult:
        destination = user.email if method_type == MfaMethodType.EMAIL else user.phone
        masked = (
            mask_email(user.email) if method_type == MfaMethodType.EMAIL else mask_phone(user.phone)
        )
        method = await self.methods.get_by_user_and_type(user.id, method_type)
        if method and method.status == MfaMethodStatus.ACTIVE:
            raise MfaAlreadyEnabledError("MFA method already enabled.")
        method = method or UserMfaMethodModel(
            user_id=user.id,
            tenant_id=user.tenant_id,
            method_type=method_type,
        )
        method.status = MfaMethodStatus.PENDING
        method.destination_masked = masked
        method.disabled_at = None
        method.is_primary = False
        await self.methods.save(method)
        code = self.otp.generate()
        challenge_payload = {
            "purpose": f"{method_type.value}_enrollment",
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "method_id": str(method.id),
            "method": method_type.value,
            "attempts": 0,
            "max_attempts": settings.mfa_otp_max_attempts,
        }
        challenge_id = await self.challenges.create(
            challenge_payload, settings.mfa_otp_expire_seconds
        )
        challenge_payload["otp_hash"] = self.otp.hash_code(code, salt=challenge_id)
        await self.challenges.update(
            challenge_id, challenge_payload, settings.mfa_otp_expire_seconds
        )
        if method_type == MfaMethodType.EMAIL:
            await self.email_sender.send_code(destination, code)
        else:
            await self.sms_sender.send_code(destination or "", code)
        return OtpSetupResult(
            method_id=method.id,
            challenge_id=challenge_id,
            destination=masked,
            expires_in=settings.mfa_otp_expire_seconds,
        )


class ConfirmOtpEnrollment:
    def __init__(
        self,
        methods: MfaMethodRepository,
        recovery_codes: MfaRecoveryCodeRepository,
        sessions: AuthSessionRepository,
        challenges: MfaChallengeStore,
        otp: OtpService,
        recovery_service: RecoveryCodeService,
    ) -> None:
        self.methods = methods
        self.recovery_codes = recovery_codes
        self.sessions = sessions
        self.challenges = challenges
        self.otp = otp
        self.recovery_service = recovery_service

    async def execute(
        self, user: object, method_type: MfaMethodType, challenge_id: str, code: str
    ) -> RecoveryCodesResult | None:
        challenge = await self.challenges.get(challenge_id)
        if challenge is None or challenge.get("purpose") != f"{method_type.value}_enrollment":
            raise MfaChallengeExpiredError("MFA challenge expired.")
        attempts = int(challenge.get("attempts", 0))
        if attempts >= int(challenge.get("max_attempts", settings.mfa_otp_max_attempts)):
            raise MfaMethodNotActiveError("MFA challenge locked.")
        if not self.otp.verify(
            code, salt=challenge_id, expected_hash=str(challenge.get("otp_hash"))
        ):
            challenge["attempts"] = attempts + 1
            await self.challenges.update(challenge_id, challenge, settings.mfa_otp_expire_seconds)
            raise MfaInvalidCodeError("Invalid MFA code.")
        method = await self.methods.get_by_id_for_user(
            UUID(challenge["method_id"]), user.id, user.tenant_id
        )
        if method is None:
            raise MfaMethodNotFoundError("MFA method not found.")
        active_methods = await self.methods.list_active_for_user(user.id, user.tenant_id)
        if not active_methods:
            await self.methods.unset_primary_for_user(user.id)
            method.is_primary = True
        method.status = MfaMethodStatus.ACTIVE
        method.verified_at = utc_now()
        method.disabled_at = None
        await self.methods.save(method)
        await self.challenges.delete(challenge_id)
        await self.sessions.revoke_all_for_user(user.id, utc_now())
        if not await self.recovery_codes.list_active_for_user(user.id, user.tenant_id):
            return await GenerateRecoveryCodes(self.recovery_codes, self.recovery_service).execute(
                user
            )
        return None


class SetPrimaryMfaMethod:
    def __init__(self, methods: MfaMethodRepository) -> None:
        self.methods = methods

    async def execute(self, user: object, method_id: UUID) -> None:
        method = await self.methods.get_by_id_for_user(method_id, user.id, user.tenant_id)
        if method is None:
            raise MfaMethodNotFoundError("MFA method not found.")
        if method.status != MfaMethodStatus.ACTIVE:
            raise MfaMethodNotActiveError("MFA method is not active.")
        await self.methods.unset_primary_for_user(user.id)
        method.is_primary = True
        await self.methods.save(method)


class DisableMfaMethod:
    def __init__(self, methods: MfaMethodRepository, sessions: AuthSessionRepository) -> None:
        self.methods = methods
        self.sessions = sessions

    async def execute(self, user: object, method_id: UUID) -> None:
        method = await self.methods.get_by_id_for_user(method_id, user.id, user.tenant_id)
        if method is None:
            raise MfaMethodNotFoundError("MFA method not found.")
        method.status = MfaMethodStatus.DISABLED
        method.is_primary = False
        method.disabled_at = utc_now()
        await self.methods.save(method)
        active = await self.methods.list_active_for_user(user.id, user.tenant_id)
        if active and not any(item.is_primary for item in active):
            active[0].is_primary = True
            await self.methods.save(active[0])
        await self.sessions.revoke_all_for_user(user.id, utc_now())


class DisableMfa:
    def __init__(
        self,
        methods: MfaMethodRepository,
        recovery_codes: MfaRecoveryCodeRepository,
        sessions: AuthSessionRepository,
        challenges: MfaChallengeStore,
        password_service: PasswordService,
    ) -> None:
        self.methods = methods
        self.recovery_codes = recovery_codes
        self.sessions = sessions
        self.challenges = challenges
        self.password_service = password_service

    async def execute(self, user: object, current_password: str) -> None:
        if not self.password_service.verify(current_password, user.password_hash):
            raise MfaInvalidCodeError("Invalid MFA disable confirmation.")
        active = await self.methods.list_active_for_user(user.id, user.tenant_id)
        if not active:
            raise MfaNotEnabledError("MFA is not enabled.")
        await self.methods.disable_all_for_user(user.id, utc_now())
        await self.recovery_codes.invalidate_all_for_user(user.id, utc_now())
        await self.challenges.revoke_user_challenges(user.id)
        await self.sessions.revoke_all_for_user(user.id, utc_now())


class GenerateRecoveryCodes:
    def __init__(
        self,
        recovery_codes: MfaRecoveryCodeRepository,
        recovery_service: RecoveryCodeService,
    ) -> None:
        self.recovery_codes = recovery_codes
        self.recovery_service = recovery_service

    async def execute(self, user: object) -> RecoveryCodesResult:
        await self.recovery_codes.invalidate_all_for_user(user.id, utc_now())
        plain_codes = self.recovery_service.generate_codes()
        models = [
            MfaRecoveryCodeModel(
                user_id=user.id,
                tenant_id=user.tenant_id,
                code_hash=self.recovery_service.hash_code(user.id, code),
            )
            for code in plain_codes
        ]
        await self.recovery_codes.create_many(models)
        return RecoveryCodesResult(codes=plain_codes)
