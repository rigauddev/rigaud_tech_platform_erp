from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    BLOCKED = "blocked"

    @property
    def allows_login(self) -> bool:
        return self == UserStatus.ACTIVE
