import pyotp
import pytest

from app.modules.auth.application.mfa_services import (
    OtpService,
    RecoveryCodeService,
    SecretEncryptionService,
    TotpService,
    mask_email,
    mask_phone,
)


@pytest.mark.unit
def test_totp_secret_is_encrypted_and_verifiable() -> None:
    totp = TotpService(SecretEncryptionService())
    enrollment = totp.begin_enrollment("user@example.com")

    assert enrollment.secret not in enrollment.encrypted_secret
    assert "otpauth://totp/" in enrollment.provisioning_uri
    assert totp.verify(enrollment.encrypted_secret, pyotp.TOTP(enrollment.secret).now())


@pytest.mark.unit
def test_otp_hash_does_not_expose_code() -> None:
    otp = OtpService()
    code = otp.generate()
    code_hash = otp.hash_code(code, salt="challenge")

    assert code not in code_hash
    assert otp.verify(code, salt="challenge", expected_hash=code_hash)
    assert not otp.verify("000000", salt="challenge", expected_hash=code_hash)


@pytest.mark.unit
def test_recovery_code_hash_and_masks() -> None:
    service = RecoveryCodeService()
    codes = service.generate_codes(2)

    assert len(codes) == 2
    assert mask_email("luis@example.com") == "l***@example.com"
    assert mask_phone("+55 75 98216-5869") == "***5869"
