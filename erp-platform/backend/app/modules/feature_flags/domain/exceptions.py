class FeatureFlagError(Exception):
    """Base exception for feature flag domain errors."""


class FeatureFlagNotFoundError(FeatureFlagError):
    pass


class FeatureFlagAlreadyExistsError(FeatureFlagError):
    pass
