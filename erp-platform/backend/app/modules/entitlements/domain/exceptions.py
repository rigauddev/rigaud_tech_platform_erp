class EntitlementError(Exception):
    """Base exception for entitlement domain errors."""


class EntitlementNotFoundError(EntitlementError):
    pass
