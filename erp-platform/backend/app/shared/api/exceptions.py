class ApplicationError(Exception):
    def __init__(
        self,
        code: str,
        *,
        details: dict | None = None,
        message: str | None = None,
    ) -> None:
        super().__init__(message or code)
        self.code = code
        self.details = details


class DomainError(ApplicationError):
    pass


class ValidationAppError(ApplicationError):
    pass


class AuthenticationAppError(ApplicationError):
    pass


class AuthorizationAppError(ApplicationError):
    pass


class NotFoundAppError(ApplicationError):
    pass


class ConflictAppError(ApplicationError):
    pass


class InfrastructureAppError(ApplicationError):
    pass
