from __future__ import annotations

import re
import unicodedata

from app.modules.categories.domain.exceptions import InvalidCategoryDataError

CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9_.-]{1,39}$")
SLUG_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{1,79}$")
COLOR_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")
ICON_PATTERN = re.compile(r"^[a-z0-9_.:-]{1,80}$")


def normalize_text(value: str, field_name: str, *, min_length: int = 1, max_length: int) -> str:
    normalized = " ".join(value.strip().split())
    if len(normalized) < min_length or len(normalized) > max_length:
        raise InvalidCategoryDataError(f"Invalid {field_name}.")
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
        raise InvalidCategoryDataError(f"Invalid {field_name}.")
    return normalized


def normalize_internal_code(value: str) -> str:
    normalized = value.strip().upper()
    if not CODE_PATTERN.fullmatch(normalized):
        raise InvalidCategoryDataError("Invalid internal_code.")
    return normalized


def normalize_slug(value: str | None, *, fallback_name: str) -> str:
    source = value.strip() if value else fallback_name
    normalized = unicodedata.normalize("NFKD", source)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not SLUG_PATTERN.fullmatch(slug):
        raise InvalidCategoryDataError("Invalid slug.")
    return slug[:80]


def normalize_icon(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if not normalized:
        return None
    if not ICON_PATTERN.fullmatch(normalized):
        raise InvalidCategoryDataError("Invalid icon.")
    return normalized


def normalize_color(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if not COLOR_PATTERN.fullmatch(normalized):
        raise InvalidCategoryDataError("Invalid color.")
    return normalized.upper()


def normalize_display_order(value: int) -> int:
    if value < 0:
        raise InvalidCategoryDataError("Invalid display_order.")
    return value
