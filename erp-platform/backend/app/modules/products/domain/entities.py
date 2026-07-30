from enum import StrEnum


class ProductType(StrEnum):
    SIMPLE = "simple"
    SERVICE = "service"
    PREPARED_ITEM = "prepared_item"


class ProductStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class UnitOfMeasure(StrEnum):
    UNIT = "unit"
    KG = "kg"
    G = "g"
    L = "l"
    ML = "ml"
    PORTION = "portion"
