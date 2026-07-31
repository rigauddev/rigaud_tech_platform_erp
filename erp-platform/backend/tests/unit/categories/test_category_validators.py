import pytest

from app.modules.categories.application.validators import (
    normalize_color,
    normalize_icon,
    normalize_internal_code,
    normalize_slug,
    normalize_text,
)
from app.modules.categories.domain.exceptions import InvalidCategoryDataError


@pytest.mark.unit
def test_category_internal_code_is_normalized() -> None:
    assert normalize_internal_code(" cat-001 ") == "CAT-001"


@pytest.mark.unit
def test_invalid_category_internal_code_is_rejected() -> None:
    with pytest.raises(InvalidCategoryDataError):
        normalize_internal_code("@@")


@pytest.mark.unit
def test_category_slug_is_generated_from_name() -> None:
    assert normalize_slug(None, fallback_name="Bebidas Geladas") == "bebidas-geladas"
    assert normalize_slug(None, fallback_name="Água com Gás") == "agua-com-gas"


@pytest.mark.unit
def test_category_visual_fields_are_normalized() -> None:
    assert normalize_color("#00aa11") == "#00AA11"
    assert normalize_icon("restaurant_menu") == "restaurant_menu"


@pytest.mark.unit
def test_category_text_is_trimmed_and_compacted() -> None:
    assert normalize_text("  Bebidas   Geladas  ", "name", max_length=120) == "Bebidas Geladas"
