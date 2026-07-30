import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.shared.observability.context import get_request_context
from app.shared.observability.sanitizer import sanitize_mapping

logger = logging.getLogger("application")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = time.perf_counter()
        logger.info(
            "http.request.started",
            extra={
                **_log_context(request),
                "event": "http.request.started",
            },
        )
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
            logger.exception(
                "http.request.failed",
                extra={
                    **_log_context(request),
                    "event": "http.request.failed",
                    "duration_ms": duration_ms,
                },
            )
            raise

        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.info(
            "http.request.completed",
            extra={
                **_log_context(request),
                "event": "http.request.completed",
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )
        return response


def _log_context(request: Request) -> dict:
    context = get_request_context()
    headers = sanitize_mapping(dict(request.headers))
    return {
        "request_id": context.request_id if context else None,
        "correlation_id": context.correlation_id if context else None,
        "tenant_id": str(context.tenant_id) if context and context.tenant_id else None,
        "user_id": str(context.user_id) if context and context.user_id else None,
        "method": request.method,
        "route": request.url.path,
        "app_module": _module_from_path(request.url.path),
        "headers": headers,
    }


def _module_from_path(path: str) -> str | None:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 3 and parts[0] == "api" and parts[1] == "v1":
        return parts[2]
    if parts:
        return parts[0]
    return None
