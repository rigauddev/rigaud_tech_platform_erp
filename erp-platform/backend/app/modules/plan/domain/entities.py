from enum import StrEnum


class PlanCode(StrEnum):
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class PlanStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class PlanCycle(StrEnum):
    MONTHLY = "monthly"
    ANNUAL = "annual"


class LimitKey(StrEnum):
    USERS = "users"
    BRANCHES = "branches"
    STORAGE_GB = "storage_gb"
    PRODUCTS = "products"
    CASH_REGISTERS = "cash_registers"
    KITCHENS = "kitchens"
    STOCK_LOCATIONS = "stock_locations"
