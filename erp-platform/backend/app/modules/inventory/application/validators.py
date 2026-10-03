from decimal import Decimal, InvalidOperation

from app.modules.inventory.domain.exceptions import (
    InventoryInvalidQuantityError,
    ReceivingDocumentInvalidDataError,
    WarehouseInvalidDataError,
    WarehouseLocationInvalidDataError,
    WarehouseZoneInvalidDataError,
)


def normalize_quantity(value: Decimal | str | int, field: str = "quantity") -> Decimal:
    try:
        quantity = Decimal(str(value)).quantize(Decimal("0.001"))
    except (InvalidOperation, ValueError) as exc:
        raise InventoryInvalidQuantityError(f"{field} is invalid.") from exc
    if quantity <= 0:
        raise InventoryInvalidQuantityError(f"{field} must be greater than zero.")
    return quantity


def normalize_reason(value: str) -> str:
    reason = value.strip()
    if len(reason) < 3 or len(reason) > 240:
        raise InventoryInvalidQuantityError("reason must have between 3 and 240 characters.")
    return reason


def normalize_warehouse_code(value: str) -> str:
    code = value.strip().upper()
    if len(code) < 2 or len(code) > 40:
        raise WarehouseInvalidDataError("warehouse code must have between 2 and 40 chars.")
    return code


def normalize_warehouse_text(value: str, field: str, *, max_length: int) -> str:
    text = value.strip()
    if not text or len(text) > max_length:
        raise WarehouseInvalidDataError(f"{field} is invalid.")
    return text


def normalize_optional_warehouse_text(
    value: str | None, field: str, *, max_length: int
) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise WarehouseInvalidDataError(f"{field} is invalid.")
    return text


def normalize_warehouse_zone_code(value: str) -> str:
    code = value.strip().upper()
    if len(code) < 2 or len(code) > 40:
        raise WarehouseZoneInvalidDataError("warehouse zone code must have between 2 and 40 chars.")
    return code


def normalize_warehouse_zone_text(value: str, field: str, *, max_length: int) -> str:
    text = value.strip()
    if not text or len(text) > max_length:
        raise WarehouseZoneInvalidDataError(f"{field} is invalid.")
    return text


def normalize_optional_warehouse_zone_text(
    value: str | None, field: str, *, max_length: int
) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise WarehouseZoneInvalidDataError(f"{field} is invalid.")
    return text


def normalize_sort_order(value: int | None) -> int:
    if value is None:
        return 0
    if value < 0 or value > 9999:
        raise WarehouseZoneInvalidDataError("sort_order must be between 0 and 9999.")
    return value


def normalize_warehouse_location_code(value: str) -> str:
    code = value.strip().upper()
    if len(code) < 2 or len(code) > 40:
        raise WarehouseLocationInvalidDataError(
            "warehouse location code must have between 2 and 40 chars."
        )
    return code


def normalize_warehouse_location_text(value: str, field: str, *, max_length: int) -> str:
    text = value.strip()
    if not text or len(text) > max_length:
        raise WarehouseLocationInvalidDataError(f"{field} is invalid.")
    return text


def normalize_optional_warehouse_location_text(
    value: str | None, field: str, *, max_length: int
) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise WarehouseLocationInvalidDataError(f"{field} is invalid.")
    return text


def normalize_location_sort_order(value: int | None) -> int:
    if value is None:
        return 0
    if value < 0 or value > 9999:
        raise WarehouseLocationInvalidDataError("sort_order must be between 0 and 9999.")
    return value


def normalize_location_capacity(value: Decimal | str | int | None) -> Decimal | None:
    if value is None:
        return None
    try:
        capacity = Decimal(str(value)).quantize(Decimal("0.001"))
    except (InvalidOperation, ValueError) as exc:
        raise WarehouseLocationInvalidDataError("capacity is invalid.") from exc
    if capacity < 0:
        raise WarehouseLocationInvalidDataError("capacity must be greater than or equal to zero.")
    return capacity


def normalize_receiving_document_number(value: str) -> str:
    document_number = value.strip().upper()
    if len(document_number) < 2 or len(document_number) > 60:
        raise ReceivingDocumentInvalidDataError("document_number must have between 2 and 60 chars.")
    return document_number


def normalize_receiving_text(value: str, field: str, *, max_length: int) -> str:
    text = value.strip()
    if not text or len(text) > max_length:
        raise ReceivingDocumentInvalidDataError(f"{field} is invalid.")
    return text


def normalize_optional_receiving_text(
    value: str | None, field: str, *, max_length: int
) -> str | None:
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    if len(text) > max_length:
        raise ReceivingDocumentInvalidDataError(f"{field} is invalid.")
    return text


def normalize_receiving_quantity(value: Decimal | str | int, field: str) -> Decimal:
    try:
        quantity = Decimal(str(value)).quantize(Decimal("0.001"))
    except (InvalidOperation, ValueError) as exc:
        raise ReceivingDocumentInvalidDataError(f"{field} is invalid.") from exc
    if quantity < 0:
        raise ReceivingDocumentInvalidDataError(f"{field} must be greater than or equal to zero.")
    return quantity


def normalize_receiving_money(value: Decimal | str | int | None, field: str) -> Decimal:
    if value is None:
        return Decimal("0.00")
    try:
        money = Decimal(str(value)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError) as exc:
        raise ReceivingDocumentInvalidDataError(f"{field} is invalid.") from exc
    if money < 0:
        raise ReceivingDocumentInvalidDataError(f"{field} must be greater than or equal to zero.")
    return money
