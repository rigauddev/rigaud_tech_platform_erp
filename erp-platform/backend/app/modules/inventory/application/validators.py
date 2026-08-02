from decimal import Decimal, InvalidOperation

from app.modules.inventory.domain.exceptions import (
    InventoryInvalidQuantityError,
    WarehouseInvalidDataError,
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
