class PlanError(Exception):
    """Base exception for plan domain errors."""


class PlanNotFoundError(PlanError):
    pass


class PlanAlreadyExistsError(PlanError):
    pass


class PlanInactiveError(PlanError):
    pass


class InvalidPlanDataError(PlanError):
    pass
