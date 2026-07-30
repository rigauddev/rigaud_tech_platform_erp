class SubscriptionError(Exception):
    """Base exception for subscription domain errors."""


class SubscriptionNotFoundError(SubscriptionError):
    pass


class SubscriptionAlreadyExistsError(SubscriptionError):
    pass


class SubscriptionInvalidTransitionError(SubscriptionError):
    pass
