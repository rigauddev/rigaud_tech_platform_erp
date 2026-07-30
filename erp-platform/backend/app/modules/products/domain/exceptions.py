class ProductError(Exception):
    """Base exception for product use cases."""


class ProductNotFoundError(ProductError):
    """Raised when a product does not exist for the current tenant."""


class ProductAlreadyExistsError(ProductError):
    """Raised when a product unique value already exists in the tenant."""


class InvalidProductDataError(ProductError):
    """Raised when product data violates validation rules."""
