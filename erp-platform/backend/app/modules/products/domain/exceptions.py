class ProductError(Exception):
    """Base exception for product use cases."""


class ProductNotFoundError(ProductError):
    """Raised when a product does not exist for the current tenant."""


class ProductAlreadyExistsError(ProductError):
    """Raised when a product unique value already exists in the tenant."""


class ProductInternalCodeAlreadyExistsError(ProductAlreadyExistsError):
    """Raised when internal_code already exists in the tenant."""


class ProductBarcodeAlreadyExistsError(ProductAlreadyExistsError):
    """Raised when barcode already exists in the tenant."""


class ProductInvalidPriceError(ProductError):
    """Raised when sale_price violates monetary rules."""


class ProductInvalidCostError(ProductError):
    """Raised when cost_price violates monetary rules."""


class ProductImageInvalidError(ProductError):
    """Raised when main image reference is invalid."""


class ProductNotAvailableError(ProductError):
    """Raised when product state does not allow sale availability."""


class InvalidProductDataError(ProductError):
    """Raised when product data violates validation rules."""
