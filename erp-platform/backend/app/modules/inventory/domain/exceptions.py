class InventoryError(Exception):
    """Base exception for inventory use cases."""


class WarehouseError(InventoryError):
    """Base exception for warehouse use cases."""


class WarehouseNotFoundError(WarehouseError):
    """Raised when a warehouse does not exist for the current tenant."""


class WarehouseAlreadyExistsError(WarehouseError):
    """Raised when a warehouse unique value already exists."""


class WarehouseCodeAlreadyExistsError(WarehouseAlreadyExistsError):
    """Raised when code already exists in the same branch."""


class WarehouseBranchRequiredError(WarehouseError):
    """Raised when the authenticated context has no active branch."""


class WarehouseInactiveError(WarehouseError):
    """Raised when operation requires an active warehouse."""


class WarehouseInvalidDataError(WarehouseError):
    """Raised when warehouse payload violates validation rules."""


class WarehouseZoneError(InventoryError):
    """Base exception for warehouse zone use cases."""


class WarehouseZoneNotFoundError(WarehouseZoneError):
    """Raised when a warehouse zone does not exist for the current tenant."""


class WarehouseZoneAlreadyExistsError(WarehouseZoneError):
    """Raised when a warehouse zone unique value already exists."""


class WarehouseZoneCodeAlreadyExistsError(WarehouseZoneAlreadyExistsError):
    """Raised when zone code already exists in the same warehouse."""


class WarehouseZoneBranchRequiredError(WarehouseZoneError):
    """Raised when the authenticated context has no active branch."""


class WarehouseZoneInvalidDataError(WarehouseZoneError):
    """Raised when warehouse zone payload violates validation rules."""


class WarehouseLocationError(InventoryError):
    """Base exception for warehouse location use cases."""


class WarehouseLocationNotFoundError(WarehouseLocationError):
    """Raised when a warehouse location does not exist for the current tenant."""


class WarehouseLocationAlreadyExistsError(WarehouseLocationError):
    """Raised when a warehouse location unique value already exists."""


class WarehouseLocationCodeAlreadyExistsError(WarehouseLocationAlreadyExistsError):
    """Raised when location code already exists in the same warehouse."""


class WarehouseLocationBarcodeAlreadyExistsError(WarehouseLocationAlreadyExistsError):
    """Raised when location barcode already exists in the tenant."""


class WarehouseLocationQrCodeAlreadyExistsError(WarehouseLocationAlreadyExistsError):
    """Raised when location QR Code already exists in the tenant."""


class WarehouseLocationBranchRequiredError(WarehouseLocationError):
    """Raised when the authenticated context has no active branch."""


class WarehouseLocationInvalidDataError(WarehouseLocationError):
    """Raised when warehouse location payload violates validation rules."""


class WarehouseZoneInactiveError(WarehouseZoneError):
    """Raised when operation requires an active warehouse zone."""


class ReceivingDocumentError(InventoryError):
    """Base exception for receiving document use cases."""


class ReceivingDocumentNotFoundError(ReceivingDocumentError):
    """Raised when a receiving document does not exist for the current tenant."""


class ReceivingDocumentAlreadyExistsError(ReceivingDocumentError):
    """Raised when a receiving document unique value already exists."""


class ReceivingDocumentNumberAlreadyExistsError(ReceivingDocumentAlreadyExistsError):
    """Raised when document number already exists in the same branch."""


class ReceivingDocumentBranchRequiredError(ReceivingDocumentError):
    """Raised when the authenticated context has no active branch."""


class ReceivingDocumentInvalidDataError(ReceivingDocumentError):
    """Raised when receiving document payload violates validation rules."""


class ReceivingDocumentItemRequiredError(ReceivingDocumentError):
    """Raised when a receiving document requires at least one item."""


class ReceivingDocumentCannotConfirmError(ReceivingDocumentError):
    """Raised when a receiving document cannot be physically confirmed."""


class PutAwayError(InventoryError):
    """Base exception for put away use cases."""


class PutAwayCannotConfirmError(PutAwayError):
    """Raised when put away cannot be confirmed."""


class InventoryBranchRequiredError(InventoryError):
    """Raised when the authenticated context has no active branch."""


class InventoryProductNotFoundError(InventoryError):
    """Raised when the product does not exist in the tenant."""


class InventoryWarehouseNotFoundError(InventoryError):
    """Raised when the warehouse does not exist in the tenant and branch."""


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
