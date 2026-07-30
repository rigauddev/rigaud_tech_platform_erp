from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = {
    "password",
    "current_password",
    "new_password",
    "password_hash",
    "access_token",
    "refresh_token",
    "refresh_token_hash",
    "authorization",
    "cookie",
    "secret",
    "jwt_secret",
    "database_url",
    "certificate",
    "private_key",
}

MASKED = "***"
MAX_TEXT_LENGTH = 512


def sanitize_mapping(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {str(key): sanitize_value(key, item) for key, item in value.items()}


def sanitize_value(key: object, value: Any) -> Any:
    key_name = str(key).lower()
    if key_name in SENSITIVE_KEYS or any(fragment in key_name for fragment in SENSITIVE_KEYS):
        return MASKED
    if isinstance(value, Mapping):
        return sanitize_mapping(value)
    if isinstance(value, list):
        return [sanitize_value(key_name, item) for item in value[:50]]
    if isinstance(value, tuple):
        return tuple(sanitize_value(key_name, item) for item in value[:50])
    if isinstance(value, str):
        return _sanitize_text(key_name, value)
    return value


def _sanitize_text(key: str, value: str) -> str:
    if len(value) > MAX_TEXT_LENGTH:
        value = f"{value[:MAX_TEXT_LENGTH]}..."
    if "email" in key and "@" in value:
        local, domain = value.split("@", 1)
        return f"{local[:1]}***@{domain}"
    if "document" in key or "cnpj" in key or "cpf" in key:
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) >= 4:
            return f"{'*' * max(len(digits) - 4, 0)}{digits[-4:]}"
    if "phone" in key or "telefone" in key:
        digits = "".join(character for character in value if character.isdigit())
        if len(digits) >= 4:
            return f"{'*' * max(len(digits) - 4, 0)}{digits[-4:]}"
    if "ip" in key and value.count(".") == 3:
        parts = value.split(".")
        return f"{parts[0]}.{parts[1]}.*.*"
    return value
