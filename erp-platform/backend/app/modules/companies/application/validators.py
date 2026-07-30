import re

from app.modules.companies.domain.exceptions import InvalidCompanyDataError

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_-]{1,19}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def normalize_text(value: str, field_name: str, *, min_length: int = 1, max_length: int) -> str:
    normalized = value.strip()
    if len(normalized) < min_length or len(normalized) > max_length:
        raise InvalidCompanyDataError(f"Invalid {field_name}.")
    return normalized


def normalize_document(document: str) -> str:
    digits = re.sub(r"\D", "", document)
    if not is_valid_cnpj(digits):
        raise InvalidCompanyDataError("Invalid document.")
    return digits


def is_valid_cnpj(document: str) -> bool:
    if not re.fullmatch(r"\d{14}", document):
        return False
    if len(set(document)) == 1:
        return False

    def calculate_digit(base: str, weights: list[int]) -> str:
        total = sum(int(digit) * weight for digit, weight in zip(base, weights, strict=True))
        remainder = total % 11
        digit = 0 if remainder < 2 else 11 - remainder
        return str(digit)

    first = calculate_digit(document[:12], [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    second = calculate_digit(document[:13], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2])
    return document[-2:] == first + second


def normalize_email(email: str | None) -> str | None:
    if email is None or not email.strip():
        return None
    normalized = email.strip().lower()
    if len(normalized) > 320 or not EMAIL_PATTERN.match(normalized):
        raise InvalidCompanyDataError("Invalid email.")
    return normalized


def normalize_phone(phone: str | None) -> str | None:
    if phone is None or not phone.strip():
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) < 8 or len(digits) > 20:
        raise InvalidCompanyDataError("Invalid phone.")
    return digits


def normalize_slug(slug: str) -> str:
    normalized = slug.strip().lower()
    if len(normalized) > 80 or not SLUG_PATTERN.fullmatch(normalized):
        raise InvalidCompanyDataError("Invalid slug.")
    return normalized


def normalize_code(code: str) -> str:
    normalized = code.strip().upper()
    if not CODE_PATTERN.fullmatch(normalized):
        raise InvalidCompanyDataError("Invalid code.")
    return normalized


def normalize_timezone(timezone: str | None) -> str:
    return normalize_text(timezone or "America/Sao_Paulo", "timezone", max_length=64)


def normalize_locale(locale: str | None) -> str:
    return normalize_text(locale or "pt-BR", "locale", max_length=16)


def normalize_currency(currency: str | None) -> str:
    normalized = (currency or "BRL").strip().upper()
    if not re.fullmatch(r"[A-Z]{3}", normalized):
        raise InvalidCompanyDataError("Invalid currency.")
    return normalized
