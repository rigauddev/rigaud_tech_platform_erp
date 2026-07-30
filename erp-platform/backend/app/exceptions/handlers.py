import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.modules.auth.domain.exceptions import AuthError
from app.modules.auth.presentation.router import auth_exception_to_response
from app.shared.api.exceptions import ApplicationError
from app.shared.api.responses import FieldError, error_response
from app.shared.observability.context import get_request_id

logger = logging.getLogger("errors")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def application_exception_handler(_: Request, exc: ApplicationError) -> JSONResponse:
        return error_response(exc.code)

    @app.exception_handler(AuthError)
    async def auth_exception_handler(_: Request, exc: AuthError) -> JSONResponse:
        return auth_exception_to_response(exc)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            return error_response("AUTH_TOKEN_INVALID")
        if exc.status_code == status.HTTP_403_FORBIDDEN:
            return error_response("AUTH_FORBIDDEN")
        return error_response("SERVICE_UNAVAILABLE", status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        _: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        errors = [
            FieldError(
                field=".".join(str(part) for part in error.get("loc", []) if part != "body"),
                code=str(error.get("type", "INVALID_FIELD")).upper(),
                message="Campo inválido.",
            )
            for error in exc.errors()
        ]
        return error_response("VALIDATION_ERROR", errors=errors)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception(
            "http.unhandled_exception",
            extra={
                "event": "http.unhandled_exception",
                "request_id": get_request_id(),
                "route": request.url.path,
                "method": request.method,
            },
        )
        return error_response("INTERNAL_SERVER_ERROR")
