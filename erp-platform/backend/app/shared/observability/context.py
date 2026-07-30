from __future__ import annotations

import re
from contextvars import ContextVar
from dataclasses import dataclass
from uuid import UUID, uuid4

MAX_CORRELATION_ID_LENGTH = 128
CORRELATION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:/@+-]{1,128}$")


@dataclass(frozen=True)
class RequestContext:
    request_id: str
    correlation_id: str | None = None
    method: str | None = None
    route: str | None = None
    tenant_id: UUID | None = None
    user_id: UUID | None = None


request_context_var: ContextVar[RequestContext | None] = ContextVar(
    "request_context",
    default=None,
)


def create_request_id() -> str:
    return str(uuid4())


def validate_correlation_id(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    normalized = value.strip()
    if len(normalized) > MAX_CORRELATION_ID_LENGTH:
        msg = "Invalid correlation id."
        raise ValueError(msg)
    if CORRELATION_ID_PATTERN.fullmatch(normalized) is None:
        msg = "Invalid correlation id."
        raise ValueError(msg)
    return normalized


def set_request_context(context: RequestContext):
    return request_context_var.set(context)


def reset_request_context(token) -> None:
    request_context_var.reset(token)


def get_request_context() -> RequestContext | None:
    return request_context_var.get()


def get_request_id() -> str | None:
    context = get_request_context()
    return context.request_id if context else None


def get_correlation_id() -> str | None:
    context = get_request_context()
    return context.correlation_id if context else None


def with_actor(*, user_id: UUID | None = None, tenant_id: UUID | None = None) -> None:
    context = get_request_context()
    if context is None:
        return
    request_context_var.set(
        RequestContext(
            request_id=context.request_id,
            correlation_id=context.correlation_id,
            method=context.method,
            route=context.route,
            tenant_id=tenant_id or context.tenant_id,
            user_id=user_id or context.user_id,
        )
    )
