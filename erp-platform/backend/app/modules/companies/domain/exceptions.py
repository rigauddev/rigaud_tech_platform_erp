class CompanyError(Exception):
    """Base exception for company domain errors."""


class CompanyNotFoundError(CompanyError):
    pass


class CompanyAlreadyExistsError(CompanyError):
    pass


class InvalidCompanyDataError(CompanyError):
    pass


class CompanyInactiveError(CompanyError):
    pass


class CompanySuspendedError(CompanyError):
    pass


class CompanyPermissionError(CompanyError):
    pass
