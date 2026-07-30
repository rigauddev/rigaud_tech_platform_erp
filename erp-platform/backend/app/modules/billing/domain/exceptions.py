class BillingError(Exception):
    """Base exception for billing domain errors."""


class BillingProviderError(BillingError):
    pass
