import pytest

from app.shared.messages.catalog import MESSAGE_CATALOG, get_message
from app.shared.observability.context import (
    create_request_id,
    validate_correlation_id,
)
from app.shared.observability.sanitizer import sanitize_mapping


@pytest.mark.unit
def test_request_id_is_uuid_like() -> None:
    assert len(create_request_id()) == 36


@pytest.mark.unit
def test_correlation_id_validation() -> None:
    assert validate_correlation_id("support-123") == "support-123"
    with pytest.raises(ValueError):
        validate_correlation_id("x" * 129)
    with pytest.raises(ValueError):
        validate_correlation_id("bad value with spaces")


@pytest.mark.unit
def test_sensitive_data_is_sanitized() -> None:
    result = sanitize_mapping(
        {
            "password": "secret",
            "email": "user@example.com",
            "document": "11222333000181",
            "nested": {"refresh_token": "token"},
        }
    )
    assert result == {
        "password": "***",
        "email": "u***@example.com",
        "document": "**********0181",
        "nested": {"refresh_token": "***"},
    }


@pytest.mark.unit
def test_message_catalog_has_stable_upper_codes() -> None:
    assert get_message("USER_CREATED").client_message
    assert all(code == code.upper() for code in MESSAGE_CATALOG)
