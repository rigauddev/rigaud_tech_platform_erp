from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class MfaMethodType(StrEnum):
    TOTP = "totp"
    EMAIL = "email"
    SMS = "sms"
    RECOVERY_CODE = "recovery_code"


class MfaMethodStatus(StrEnum):
    PENDING = "pending"
    ACTIVE = "active"
    DISABLED = "disabled"


class MfaState(StrEnum):
    DISABLED = "disabled"
    PENDING_ENROLLMENT = "pending_enrollment"
    ENABLED = "enabled"
    RECOVERY_REQUIRED = "recovery_required"


@dataclass(frozen=True)
class MfaMethodSummary:
    id: UUID
    type: MfaMethodType
    status: MfaMethodStatus
    is_primary: bool
    destination: str | None = None
    verified_at: datetime | None = None
    last_used_at: datetime | None = None


@dataclass(frozen=True)
class LoginMfaMethod:
    id: UUID
    type: MfaMethodType
    destination: str | None = None


@dataclass(frozen=True)
class LoginMfaChallenge:
    challenge_id: str
    available_methods: list[LoginMfaMethod]
    expires_in: int


@dataclass(frozen=True)
class MfaStatus:
    state: MfaState
    enabled: bool
    primary_method_id: UUID | None
    methods: list[MfaMethodSummary]
    recovery_codes_remaining: int
