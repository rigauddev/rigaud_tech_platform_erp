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
