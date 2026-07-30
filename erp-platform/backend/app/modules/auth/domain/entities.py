from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    tenant_id: UUID
    tenant_slug: str
    email: str
    is_active: bool
    is_superuser: bool
    deleted_at: datetime | None = None

    @property
    def can_authenticate(self) -> bool:
        return self.is_active and self.deleted_at is None


@dataclass(frozen=True)
class TokenPair:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
