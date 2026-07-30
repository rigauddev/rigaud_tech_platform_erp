from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
import smtplib
from dataclasses import dataclass
from datetime import UTC, datetime
from email.message import EmailMessage
from uuid import UUID

import pyotp
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.environment import Environment
from app.modules.auth.domain.exceptions import MfaProviderUnavailableError


def mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    if not domain:
        return "***"
    prefix = local[:1]
    return f"{prefix}***@{domain}"


def mask_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = "".join(character for character in phone if character.isdigit())
    if len(digits) < 4:
        return "***"
    return f"***{digits[-4:]}"


class SecretEncryptionService:
    def __init__(self, key: str | None = None) -> None:
        raw_key = key or settings.mfa_encryption_key
        if settings.app_env != Environment.PRODUCTION:
            raw_key = self._development_key(raw_key)
        if not raw_key:
            raise MfaProviderUnavailableError("MFA encryption key is not configured.")
        try:
            self._fernet = Fernet(raw_key.encode("utf-8"))
        except ValueError as exc:
            raise MfaProviderUnavailableError("Invalid MFA encryption key.") from exc

    def encrypt(self, value: str) -> str:
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, encrypted_value: str) -> str:
        try:
            return self._fernet.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise MfaProviderUnavailableError("MFA secret cannot be decrypted.") from exc

    def _development_key(self, raw_key: str) -> str:
        if raw_key:
            try:
                Fernet(raw_key.encode("utf-8"))
                return raw_key
            except ValueError:
                pass
        return base64.urlsafe_b64encode(
            hashlib.sha256(settings.jwt_secret_key.encode("utf-8")).digest()
        ).decode("utf-8")


@dataclass(frozen=True)
class TotpEnrollment:
    secret: str
    encrypted_secret: str
    provisioning_uri: str
    issuer: str


class TotpService:
    def __init__(self, encryption: SecretEncryptionService | None = None) -> None:
        self.encryption = encryption or SecretEncryptionService()

    def begin_enrollment(self, email: str) -> TotpEnrollment:
        secret = pyotp.random_base32()
        return TotpEnrollment(
            secret=secret,
            encrypted_secret=self.encryption.encrypt(secret),
            provisioning_uri=pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name=settings.mfa_totp_issuer,
            ),
            issuer=settings.mfa_totp_issuer,
        )

    def verify(self, encrypted_secret: str, code: str) -> bool:
        secret = self.encryption.decrypt(encrypted_secret)
        return pyotp.TOTP(secret).verify(code.strip(), valid_window=1)


class OtpService:
    def generate(self, length: int = 6) -> str:
        upper = 10**length
        return f"{secrets.randbelow(upper):0{length}d}"

    def hash_code(self, code: str, *, salt: str) -> str:
        return hmac.new(
            settings.jwt_secret_key.encode("utf-8"),
            f"{salt}:{code.strip()}".encode(),
            hashlib.sha256,
        ).hexdigest()

    def verify(self, code: str, *, salt: str, expected_hash: str) -> bool:
        return hmac.compare_digest(self.hash_code(code, salt=salt), expected_hash)


class RecoveryCodeService:
    def generate_codes(self, count: int | None = None) -> list[str]:
        total = count or settings.mfa_recovery_codes_count
        return [
            f"{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}" for _ in range(total)
        ]

    def hash_code(self, user_id: UUID, code: str) -> str:
        normalized = code.strip().upper().replace(" ", "")
        return hmac.new(
            settings.jwt_secret_key.encode("utf-8"),
            f"{user_id}:{normalized}".encode(),
            hashlib.sha256,
        ).hexdigest()


class DevelopmentEmailOtpSender:
    async def send_code(self, email: str, code: str) -> None:
        if settings.app_env == Environment.PRODUCTION or not settings.email_otp_dev_enabled:
            raise MfaProviderUnavailableError("Email OTP provider unavailable.")
        message = EmailMessage()
        message["Subject"] = "Código de verificação"
        message["From"] = "no-reply@rigaud.tech"
        message["To"] = email
        message.set_content(f"Seu código de verificação é: {code}")
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=5) as smtp:
                smtp.send_message(message)
        except OSError:
            return


class DevelopmentSmsOtpSender:
    async def send_code(self, phone: str, code: str) -> None:
        if settings.app_env == Environment.PRODUCTION or not settings.sms_otp_dev_enabled:
            raise MfaProviderUnavailableError("SMS OTP provider unavailable.")
        if not phone:
            raise MfaProviderUnavailableError("SMS OTP destination unavailable.")


def utc_now() -> datetime:
    return datetime.now(UTC)
