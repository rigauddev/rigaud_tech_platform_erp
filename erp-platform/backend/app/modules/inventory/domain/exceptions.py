class InventoryError(Exception):
    """Base exception for inventory use cases."""


class InventoryBranchRequiredError(InventoryError):
    """Raised when the authenticated context has no active branch."""


class InventoryProductNotFoundError(InventoryError):
    """Raised when the product does not exist in the tenant."""


class InventoryBalanceNotFoundError(InventoryError):
    """Raised when a balance projection does not exist."""


class InventoryInsufficientStockError(InventoryError):
    """Raised when an operation would make stock unavailable."""


class InventoryInvalidQuantityError(InventoryError):
    """Raised when quantity is not valid."""


class InventoryReservationNotFoundError(InventoryError):
    """Raised when a reservation does not exist for the tenant."""


class InventoryReservationInactiveError(InventoryError):
    """Raised when a reservation cannot be released or changed."""
