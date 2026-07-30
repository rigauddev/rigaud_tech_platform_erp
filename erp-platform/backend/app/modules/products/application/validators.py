from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation

from app.modules.products.domain.exceptions import InvalidProductDataError

CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{1,39}$")
BARCODE_PATTERN = re.compile(r"^[0-9A-Za-z_.-]{3,64}$")
IMAGE_URL_PATTERN = re.compile(r"^https?://[^\s]{3,500}$")
MONEY_QUANTIZE = Decimal("0.01")


def normalize_text(value: str, field_name: str, *, min_length: int = 1, max_length: int) -> str:
    normalized = " ".join(value.strip().split())
    if len(normalized) < min_length or len(normalized) > max_length:
        raise InvalidProductDataError(f"Invalid {field_name}.")
    return normalized


def normalize_optional_text(
    value: str | None,
    field_name: str,
    *,
    max_length: int,
) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None
    if len(normalized) > max_length:
        raise InvalidProductDataError(f"Invalid {field_name}.")
    return normalized


def normalize_internal_code(value: str) -> str:
    normalized = value.strip().upper()
    if not CODE_PATTERN.fullmatch(normalized):
        raise InvalidProductDataError("Invalid internal_code.")
    return normalized


def normalize_barcode(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if not BARCODE_PATTERN.fullmatch(normalized):
        raise InvalidProductDataError("Invalid barcode.")
    return normalized


def normalize_money(value: Decimal | str | int | None, field_name: str) -> Decimal:
    if value is None:
        return Decimal("0.00")
    try:
        amount = Decimal(str(value)).quantize(MONEY_QUANTIZE)
    except (InvalidOperation, ValueError) as exc:
        raise InvalidProductDataError(f"Invalid {field_name}.") from exc
    if amount < Decimal("0.00"):
        raise InvalidProductDataError(f"Invalid {field_name}.")
    return amount


def normalize_image_url(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if not IMAGE_URL_PATTERN.fullmatch(normalized):
        raise InvalidProductDataError("Invalid main_image_url.")
    return normalized
