import asyncio

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.database.session import check_database_connection
from app.shared.presentation.schemas import DatabaseHealthResponse, HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok",
        environment=settings.app_env,
        version=settings.app_version,
    )


@router.get(
    "/database",
    response_model=DatabaseHealthResponse,
    summary="Database health check",
)
async def database_health_check() -> DatabaseHealthResponse | JSONResponse:
    try:
        is_connected = await asyncio.wait_for(
            check_database_connection(),
            timeout=settings.database_health_timeout_seconds,
        )
    except (TimeoutError, OSError):
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=DatabaseHealthResponse(
                status="unhealthy",
                database="unreachable",
            ).model_dump(),
        )

    if not is_connected:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=DatabaseHealthResponse(
                status="unhealthy",
                database="unreachable",
            ).model_dump(),
        )

    return DatabaseHealthResponse(status="healthy", database="reachable")
