import logging
import sys

from pythonjsonlogger import json as jsonlogger

from app.core.config import settings
from app.shared.observability.context import get_request_context
from app.shared.observability.sanitizer import sanitize_mapping


class StructuredLogFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        context = get_request_context()
        defaults = {
            "event": getattr(record, "event", record.getMessage()),
            "request_id": context.request_id if context else None,
            "correlation_id": context.correlation_id if context else None,
            "tenant_id": str(context.tenant_id) if context and context.tenant_id else None,
            "user_id": str(context.user_id) if context and context.user_id else None,
            "service": settings.app_name,
            "environment": str(settings.app_env),
            "method": None,
            "route": None,
            "status_code": None,
            "duration_ms": None,
            "app_module": None,
        }
        for key, value in defaults.items():
            if not hasattr(record, key):
                setattr(record, key, value)
        if hasattr(record, "headers") and isinstance(record.headers, dict):
            record.headers = sanitize_mapping(record.headers)
        return True


def configure_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(settings.log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(StructuredLogFilter())
    handler.setFormatter(
        jsonlogger.JsonFormatter(
            "%(asctime)s %(levelname)s %(name)s %(event)s %(message)s "
            "%(request_id)s %(correlation_id)s %(service)s %(environment)s "
            "%(method)s %(route)s %(status_code)s %(duration_ms)s %(tenant_id)s "
            "%(user_id)s %(app_module)s",
        )
    )

    root_logger.addHandler(handler)

    for logger_name in (
        settings.application_log_name,
        settings.error_log_name,
        settings.audit_log_name,
    ):
        logging.getLogger(logger_name).setLevel(settings.log_level.upper())


def get_application_logger() -> logging.Logger:
    return logging.getLogger(settings.application_log_name)


def get_error_logger() -> logging.Logger:
    return logging.getLogger(settings.error_log_name)


def get_audit_logger() -> logging.Logger:
    return logging.getLogger(settings.audit_log_name)
