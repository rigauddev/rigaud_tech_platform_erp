import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.core.config import settings
from app.security.jwt import create_auth_access_token, decode_auth_access_token


@dataclass(frozen=True)
class RefreshToken:
    token: str
    token_hash: str
    expires_at: datetime


class TokenService:
    def create_access_token(self, user_id: UUID, tenant_id: UUID) -> str:
        return create_auth_access_token(user_id=user_id, tenant_id=tenant_id)

    def decode_access_token(self, token: str) -> dict[str, object]:
        return decode_auth_access_token(token)

    def create_refresh_token(self) -> RefreshToken:
        token = secrets.token_urlsafe(48)
        return RefreshToken(
            token=token,
            token_hash=self.hash_refresh_token(token),
            expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days),
        )

    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    @property
    def access_token_expires_in(self) -> int:
        return settings.jwt_access_token_expire_minutes * 60
