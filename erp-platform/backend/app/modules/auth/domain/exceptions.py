class AuthError(Exception):
    """Base exception for authentication use cases."""


class InvalidCredentialsError(AuthError):
    """Raised for invalid login credentials without exposing which field failed."""


class InactiveUserError(AuthError):
    """Raised when a valid user cannot authenticate because it is inactive."""


class BlockedUserError(AuthError):
    """Raised when a valid user cannot authenticate because it is blocked."""


class InvalidTokenError(AuthError):
    """Raised when a token is malformed, invalid, or has unexpected claims."""


class ExpiredTokenError(InvalidTokenError):
    """Raised when a token is expired."""


class RevokedTokenError(InvalidTokenError):
    """Raised when a refresh token session has been revoked."""


class TenantNotFoundError(AuthError):
    """Raised when tenant resolution fails."""


class TenantInactiveError(AuthError):
    """Raised when tenant is inactive."""


class TenantSuspendedError(AuthError):
    """Raised when tenant is suspended."""


class AuthenticationRequiredError(AuthError):
    """Raised when an endpoint requires an authenticated user."""


class MfaRequiredError(AuthError):
    """Raised when login requires a second authentication factor."""


class MfaInvalidCodeError(AuthError):
    """Raised when an MFA code is invalid."""


class MfaExpiredCodeError(AuthError):
    """Raised when an MFA code is expired."""


class MfaChallengeExpiredError(AuthError):
    """Raised when an MFA challenge is expired or missing."""


class MfaChallengeLockedError(AuthError):
    """Raised when an MFA challenge exceeded the attempt limit."""


class MfaMethodNotFoundError(AuthError):
    """Raised when an MFA method cannot be found for the current user."""


class MfaMethodNotActiveError(AuthError):
    """Raised when an MFA method is not active."""


class MfaAlreadyEnabledError(AuthError):
    """Raised when enabling an already active MFA method."""


class MfaNotEnabledError(AuthError):
    """Raised when MFA is required but no active method exists."""


class MfaProviderUnavailableError(AuthError):
    """Raised when an MFA delivery or challenge provider is unavailable."""


class MfaRateLimitedError(AuthError):
    """Raised when MFA operation limits are exceeded."""


class MfaRecoveryCodeInvalidError(AuthError):
    """Raised when a recovery code is invalid or already used."""
