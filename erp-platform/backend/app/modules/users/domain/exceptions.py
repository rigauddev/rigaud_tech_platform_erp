class UserError(Exception):
    """Base exception for user use cases."""


class UserNotFoundError(UserError):
    """Raised when a user does not exist or is soft deleted."""


class UserAlreadyExistsError(UserError):
    """Raised when an email already exists for the same tenant."""


class UserPermissionError(UserError):
    """Raised when the current actor cannot perform a user action."""


class InvalidUserDataError(UserError):
    """Raised when user data violates validation rules."""


class InvalidPasswordError(UserError):
    """Raised when a password operation violates policy or confirmation."""
