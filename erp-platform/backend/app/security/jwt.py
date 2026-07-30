from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from app.core.config import settings
from app.modules.auth.domain.exceptions import ExpiredTokenError, InvalidTokenError


def create_access_token(subject: str, expires_delta: timedelta | None = None) -> str:
    expires_at = datetime.now(UTC) + (
        expires_delta or timedelta(minutes=settings.jwt_access_token_expire_minutes)
    )
    payload: dict[str, Any] = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def create_auth_access_token(user_id: UUID, tenant_id: UUID) -> str:
    issued_at = datetime.now(UTC)
    expires_at = issued_at + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "token_type": "access",
        "iat": int(issued_at.timestamp()),
        "exp": expires_at,
        "jti": str(uuid4()),
    }
    if settings.jwt_issuer:
        payload["iss"] = settings.jwt_issuer
    if settings.jwt_audience:
        payload["aud"] = settings.jwt_audience
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_auth_access_token(token: str) -> dict[str, Any]:
    issuer = settings.jwt_issuer or None
    audience = settings.jwt_audience or None
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            issuer=issuer,
            audience=audience,
            options={"verify_aud": audience is not None},
        )
    except ExpiredSignatureError as exc:
        raise ExpiredTokenError("Token expired.") from exc
    except JWTError as exc:
        raise InvalidTokenError("Invalid token.") from exc

    required_claims = {"sub", "tenant_id", "token_type", "iat", "exp", "jti"}
    if not required_claims.issubset(payload):
        raise InvalidTokenError("Missing token claims.")
    if payload["token_type"] != "access":
        raise InvalidTokenError("Invalid token type.")
    return payload
