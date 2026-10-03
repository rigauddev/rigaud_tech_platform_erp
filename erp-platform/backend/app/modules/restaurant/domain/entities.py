from enum import StrEnum


class RestaurantTableStatus(StrEnum):
    AVAILABLE = "available"
    OCCUPIED = "occupied"
    RESERVED = "reserved"
    ORDER_PENDING = "order_pending"
    KITCHEN = "kitchen"
    WAITING_PAYMENT = "waiting_payment"
    CLEANING = "cleaning"
    BLOCKED = "blocked"


class RestaurantTableShape(StrEnum):
    SQUARE = "square"
    ROUND = "round"
    RECTANGLE = "rectangle"


class RestaurantSectorType(StrEnum):
    DINING_ROOM = "dining_room"
    OUTDOOR = "outdoor"
    BAR = "bar"
    VIP = "vip"
    COUNTER = "counter"
    OTHER = "other"


class RestaurantStaffRole(StrEnum):
    WAITER = "waiter"
    ATTENDANT = "attendant"
    MANAGER = "manager"


class RestaurantStaffStatus(StrEnum):
    AVAILABLE = "available"
    SERVING = "serving"
    PAUSED = "paused"
    OFFLINE = "offline"
