from enum import StrEnum


class WarehouseStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


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
