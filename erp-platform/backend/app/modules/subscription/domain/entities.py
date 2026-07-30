from enum import StrEnum


class SubscriptionStatus(StrEnum):
    TRIAL = "trial"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

    @property
    def allows_regular_usage(self) -> bool:
        return self in {
            SubscriptionStatus.TRIAL,
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.PAST_DUE,
        }


class SubscriptionChangeType(StrEnum):
    UPGRADE = "upgrade"
    DOWNGRADE = "downgrade"
    CHANGE = "change"
