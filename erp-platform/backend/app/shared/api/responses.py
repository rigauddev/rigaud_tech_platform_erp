from __future__ import annotations

from datetime import UTC, datetime
from math import ceil
from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict

from app.shared.messages.catalog import get_message
from app.shared.observability.context import get_correlation_id, get_request_id


class FieldError(BaseModel):
    field: str
    code: str
    message: str


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int

    @classmethod
    def from_total(cls, *, page: int, page_size: int, total: int) -> PaginationMeta:
        return cls(
            page=page,
            page_size=page_size,
            total=total,
            total_pages=ceil(total / page_size) if page_size else 0,
        )


class ApiSuccessResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = True
    code: str
    message: str
    data: Any = None
    meta: dict[str, Any] | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    timestamp: str


class ApiErrorResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    success: bool = False
    code: str
    message: str
    errors: list[FieldError] | None = None
    request_id: str | None = None
    correlation_id: str | None = None
    timestamp: str


def utc_timestamp() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def success_response(
    code: str,
    *,
    data: Any = None,
    meta: BaseModel | dict[str, Any] | None = None,
    status_code: int | None = None,
) -> JSONResponse:
    message = get_message(code)
    meta_data = meta.model_dump(mode="json") if isinstance(meta, BaseModel) else meta
    content = ApiSuccessResponse(
        code=message.code,
        message=message.client_message,
        data=data,
        meta=meta_data,
        request_id=get_request_id(),
        correlation_id=get_correlation_id(),
        timestamp=utc_timestamp(),
    ).model_dump(mode="json")
    if isinstance(data, dict):
        content.update(data)
    if isinstance(data, list):
        content["items"] = data
    if meta_data:
        content.update(meta_data)
    return JSONResponse(status_code=status_code or message.http_status, content=content)


def error_response(
    code: str,
    *,
    errors: list[FieldError] | None = None,
    status_code: int | None = None,
) -> JSONResponse:
    message = get_message(code)
    content = ApiErrorResponse(
        code=message.code,
        message=message.client_message,
        errors=errors,
        request_id=get_request_id(),
        correlation_id=get_correlation_id(),
        timestamp=utc_timestamp(),
    ).model_dump(mode="json")
    return JSONResponse(status_code=status_code or message.http_status, content=content)
