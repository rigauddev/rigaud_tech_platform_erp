class CategoryError(Exception):
    """Base error for category operations."""


class InvalidCategoryDataError(CategoryError):
    """Raised when category data is invalid."""


class CategoryNotFoundError(CategoryError):
    """Raised when a category does not exist in the active tenant."""


class CategoryAlreadyExistsError(CategoryError):
    """Raised when a category conflicts with an existing category."""


class CategoryInternalCodeAlreadyExistsError(CategoryAlreadyExistsError):
    """Raised when the internal code is already used in the tenant."""


class CategorySlugAlreadyExistsError(CategoryAlreadyExistsError):
    """Raised when the slug is already used in the tenant."""


class CategoryCycleError(CategoryError):
    """Raised when a parent relationship would create a cycle."""


class CategoryInUseError(CategoryError):
    """Raised when a category cannot be removed because it is in use."""
