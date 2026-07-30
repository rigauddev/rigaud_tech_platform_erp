from enum import StrEnum


class CompanyStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

    @property
    def allows_login(self) -> bool:
        return self == CompanyStatus.ACTIVE
