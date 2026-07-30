import re

from app.modules.auth.application.email import normalize_email

PHONE_RE = re.compile(r"^[0-9+() .-]{8,32}$")


def normalize_optional_text(value: str | None, field_name: str, *, max_length: int) -> str | None:
    if value is None:
        return None
    normalized = " ".join(value.strip().split())
    if not normalized:
        return None
    if len(normalized) > max_length:
        msg = f"{field_name} is too long."
        raise ValueError(msg)
    return normalized


def normalize_phone(value: str | None) -> str | None:
    phone = normalize_optional_text(value, "phone", max_length=32)
    if phone is None:
        return None
    if not PHONE_RE.fullmatch(phone):
        msg = "phone is invalid."
        raise ValueError(msg)
    return phone


def normalize_user_email(value: str) -> str:
    return normalize_email(value)
