from typing import Any

from pydantic import BaseModel, ConfigDict


class BaseResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorResponse(BaseResponse):
    code: str
    message: str
    details: dict[str, Any] | None = None
    request_id: str | None = None


class HealthResponse(BaseResponse):
    status: str
    environment: str
    version: str


class DatabaseHealthResponse(BaseResponse):
    status: str
    database: str
