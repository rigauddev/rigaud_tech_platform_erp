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
    PUTAWAY_PENDING = "putaway_pending"
    AVAILABLE = "available"
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
    RECEIPT = "receipt"
    PUTAWAY = "putaway"
    ADJUSTMENT_IN = "adjustment_in"
    ADJUSTMENT_OUT = "adjustment_out"
    RESERVATION_CREATED = "reservation_created"
    RESERVATION_RELEASED = "reservation_released"
    COUNT = "count"
    TRANSFER_OUT = "transfer_out"
    TRANSFER_IN = "transfer_in"


class InventoryMovementStatus(StrEnum):
    CONFIRMED = "confirmed"


class InventoryAdjustmentType(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"


class InventoryAdjustmentStatus(StrEnum):
    CONFIRMED = "confirmed"


class InventoryAdjustmentReason(StrEnum):
    CORRECTION = "correction"
    DAMAGE = "damage"
    LOSS = "loss"
    EXPIRY = "expiry"
    OPENING_BALANCE = "opening_balance"
    RETURN = "return"
    REVERSAL = "reversal"


class InventoryReservationStatus(StrEnum):
    ACTIVE = "active"
    RELEASED = "released"
    CANCELLED = "cancelled"


class InventoryCountStatus(StrEnum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    CANCELLED = "cancelled"


class InventoryTransferStatus(StrEnum):
    DRAFT = "draft"
    REQUESTED = "requested"
    IN_TRANSIT = "in_transit"
    RECEIVED = "received"
    CANCELLED = "cancelled"
