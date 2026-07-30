from decimal import Decimal

import pytest

from app.modules.products.application.validators import (
    normalize_barcode,
    normalize_internal_code,
    normalize_money,
    normalize_text,
)
from app.modules.products.domain.exceptions import (
    InvalidProductDataError,
    ProductInvalidCostError,
    ProductInvalidPriceError,
)


@pytest.mark.unit
def test_internal_code_is_normalized() -> None:
    assert normalize_internal_code(" prd-001 ") == "PRD-001"


@pytest.mark.unit
def test_invalid_internal_code_is_rejected() -> None:
    with pytest.raises(InvalidProductDataError):
        normalize_internal_code("@@")


@pytest.mark.unit
def test_null_barcode_is_allowed() -> None:
    assert normalize_barcode(None) is None
    assert normalize_barcode("   ") is None


@pytest.mark.unit
def test_money_uses_decimal_and_rejects_negative_values() -> None:
    assert normalize_money("10.129", "sale_price") == Decimal("10.13")
    assert normalize_money("0.00", "sale_price") == Decimal("0.00")
    assert normalize_money("0.01", "sale_price") == Decimal("0.01")
    assert normalize_money("9999999999.99", "sale_price") == Decimal("9999999999.99")
    with pytest.raises(ProductInvalidPriceError):
        normalize_money("-0.01", "sale_price")
    with pytest.raises(ProductInvalidCostError):
        normalize_money("invalid", "cost_price")


@pytest.mark.unit
def test_text_is_trimmed_and_compacted() -> None:
    assert normalize_text("  Produto   Teste  ", "name", max_length=160) == "Produto Teste"
