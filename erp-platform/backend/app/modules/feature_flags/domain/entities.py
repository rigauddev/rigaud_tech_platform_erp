from enum import StrEnum


class FeatureFlagScope(StrEnum):
    GLOBAL = "global"
    TENANT = "tenant"


class FeatureFlagStatus(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
