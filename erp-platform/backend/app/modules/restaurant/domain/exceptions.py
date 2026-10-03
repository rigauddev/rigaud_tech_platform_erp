class RestaurantError(Exception):
    """Base exception for the Restaurant Operations module."""


class RestaurantBranchRequiredError(RestaurantError):
    pass


class RestaurantFloorNotFoundError(RestaurantError):
    pass


class RestaurantFloorCodeAlreadyExistsError(RestaurantError):
    pass


class RestaurantTableNotFoundError(RestaurantError):
    pass


class RestaurantTableNumberAlreadyExistsError(RestaurantError):
    pass


class RestaurantInvalidDataError(RestaurantError):
    pass
