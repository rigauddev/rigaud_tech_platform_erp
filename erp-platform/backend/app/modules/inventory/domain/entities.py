from enum import StrEnum


class WarehouseStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class WarehouseZoneStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class WarehouseLocationStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ReceivingDocumentStatus(StrEnum):
    DRAFT = "draft"
    EXPECTED = "expected"
    RECEIVING = "receiving"
    PARTIAL = "partial"
    RECEIVED = "received"
    CANCELLED = "cancelled"


class WarehouseZoneType(StrEnum):
    RECEIVING = "receiving"
    SHIPPING = "shipping"
    STORAGE = "storage"
    PRODUCTION = "production"
    QUARANTINE = "quarantine"
    PICKING = "picking"
    DISPLAY = "display"
    OTHER = "other"


class InventoryMovementType(StrEnum):
    ADJUSTMENT_IN = "adjustment_in"
    ADJUSTMENT_OUT = "adjustment_out"
    RESERVATION_CREATED = "reservation_created"
    RESERVATION_RELEASED = "reservation_released"


class InventoryMovementStatus(StrEnum):
    CONFIRMED = "confirmed"


class InventoryAdjustmentType(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"


class InventoryAdjustmentStatus(StrEnum):
    CONFIRMED = "confirmed"


class InventoryReservationStatus(StrEnum):
    ACTIVE = "active"
    RELEASED = "released"
    CANCELLED = "cancelled"
