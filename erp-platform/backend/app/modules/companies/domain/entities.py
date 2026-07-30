from enum import StrEnum


class CompanyStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

    @property
    def allows_login(self) -> bool:
        return self == CompanyStatus.ACTIVE


class BranchType(StrEnum):
    HEADQUARTERS = "headquarters"
    STORE = "store"
    WAREHOUSE = "warehouse"


class BranchStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class MembershipStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class CompanyRole(StrEnum):
    COMPANY_ADMIN = "company_admin"
    MEMBER = "member"


class BranchRole(StrEnum):
    BRANCH_MANAGER = "branch_manager"
    BRANCH_OPERATOR = "branch_operator"


class AccessScope(StrEnum):
    ALL_BRANCHES = "all_branches"
    SELECTED_BRANCHES = "selected_branches"
