from decimal import Decimal, InvalidOperation

from app.modules.inventory.domain.exceptions import InventoryInvalidQuantityError


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
