from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.api.v1.routes.health import router as health_router
from app.core.config import settings
from app.core.database import dispose_database_engine
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.core.openapi import openapi_tags
from app.middlewares.config import register_middlewares


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:
    settings.validate_security()
    yield
    await dispose_database_engine()


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        debug=settings.debug_enabled,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        openapi_tags=openapi_tags,
        lifespan=lifespan,
    )

    register_middlewares(app)
    register_exception_handlers(app)
    app.include_router(health_router, prefix="/health", tags=["Health"])
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
