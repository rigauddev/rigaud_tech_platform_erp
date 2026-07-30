import logging
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.shared.api.responses import error_response
from app.shared.observability.context import (
    RequestContext,
    create_request_id,
    reset_request_context,
    set_request_context,
    validate_correlation_id,
)
from app.shared.observability.context import (
    get_request_id as current_request_id,
)

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
logger = logging.getLogger("application")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = create_request_id()
        try:
            correlation_id = validate_correlation_id(request.headers.get(CORRELATION_ID_HEADER))
        except ValueError:
            token = set_request_context(
                RequestContext(
                    request_id=request_id,
                    method=request.method,
                    route=request.url.path,
                )
            )
            try:
                response = error_response("VALIDATION_ERROR")
            finally:
                reset_request_context(token)
            response.headers[REQUEST_ID_HEADER] = request_id
            return response

        token = set_request_context(
            RequestContext(
                request_id=request_id,
                correlation_id=correlation_id,
                method=request.method,
                route=request.url.path,
            )
        )
        try:
            response = await call_next(request)
        finally:
            reset_request_context(token)

        response.headers[REQUEST_ID_HEADER] = request_id
        if correlation_id:
            response.headers[CORRELATION_ID_HEADER] = correlation_id
        return response


def get_request_id() -> str | None:
    return current_request_id()
