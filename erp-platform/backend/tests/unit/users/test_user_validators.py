import pytest

from app.modules.users.application.validators import (
    normalize_optional_text,
    normalize_phone,
    normalize_user_email,
)


@pytest.mark.unit
def test_user_email_is_normalized() -> None:
    assert normalize_user_email(" USER@EXAMPLE.COM ") == "user@example.com"


@pytest.mark.unit
def test_optional_text_is_trimmed_and_collapsed() -> None:
    assert (
        normalize_optional_text("  Maria   Silva  ", "first_name", max_length=80) == "Maria Silva"
    )


@pytest.mark.unit
def test_invalid_phone_is_rejected() -> None:
    with pytest.raises(ValueError):
        normalize_phone("abc")
