from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.modules.auth.application.email import normalize_email, normalize_tenant
from app.modules.auth.application.passwords import PasswordService
from app.modules.auth.application.tokens import TokenService
from app.modules.auth.domain.exceptions import InvalidTokenError


@pytest.mark.unit
def test_normalize_email() -> None:
    assert normalize_email(" USER@Example.COM ") == "user@example.com"


@pytest.mark.unit
def test_normalize_email_rejects_invalid_format() -> None:
    with pytest.raises(ValueError):
        normalize_email("invalid-email")


@pytest.mark.unit
def test_normalize_tenant() -> None:
    assert normalize_tenant(" Rigaud-Demo ") == "rigaud-demo"


@pytest.mark.unit
def test_password_hash_verify_and_rehash_check() -> None:
    service = PasswordService()
    password_hash = service.hash("Senha123")

    assert password_hash != "Senha123"
    assert service.verify("Senha123", password_hash) is True
    assert service.verify("errada123", password_hash) is False
    assert service.needs_rehash(password_hash) is False


@pytest.mark.unit
def test_password_policy_rejects_invalid_password() -> None:
    service = PasswordService()

    with pytest.raises(ValueError):
        service.hash("short1")
    with pytest.raises(ValueError):
        service.hash("semnumeros")
    with pytest.raises(ValueError):
        service.hash("12345678")


@pytest.mark.unit
def test_access_token_generation_and_validation() -> None:
    service = TokenService()
    user_id = uuid4()
    tenant_id = uuid4()

    token = service.create_access_token(user_id, tenant_id)
    payload = service.decode_access_token(token)

    assert payload["sub"] == str(user_id)
    assert payload["tenant_id"] == str(tenant_id)
    assert payload["token_type"] == "access"
    assert payload["jti"]


@pytest.mark.unit
def test_access_token_rejects_refresh_type(monkeypatch: pytest.MonkeyPatch) -> None:
    from jose import jwt

    from app.core.config import settings

    now = datetime.now(UTC)
    payload = {
        "sub": str(uuid4()),
        "tenant_id": str(uuid4()),
        "token_type": "refresh",
        "iat": int(now.timestamp()),
        "exp": now + timedelta(minutes=5),
        "jti": str(uuid4()),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    with pytest.raises(InvalidTokenError):
        TokenService().decode_access_token(token)


@pytest.mark.unit
def test_refresh_token_is_hashed() -> None:
    service = TokenService()
    refresh = service.create_refresh_token()

    assert refresh.token
    assert refresh.token_hash == service.hash_refresh_token(refresh.token)
    assert refresh.token_hash != refresh.token
