from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.environment import Environment
from app.database import get_async_session
from app.shared.api.responses import error_response, success_response
from app.shared.demo.service import DemoSeeder

router = APIRouter(prefix="/demo", tags=["Demo"])

AsyncSessionDependency = Annotated[AsyncSession, Depends(get_async_session)]


def _demo_available() -> bool:
    return settings.app_env in {Environment.LOCAL, Environment.DEVELOPMENT, Environment.TEST}


def _blocked_response():
    return error_response("DEMO_NOT_AVAILABLE", status_code=404)


@router.get("/status")
async def demo_status(session: AsyncSessionDependency):
    if not _demo_available():
        return _blocked_response()
    return success_response("DEMO_STATUS_RETRIEVED", data=await DemoSeeder(session).status())


@router.get("/install")
async def demo_install(session: AsyncSessionDependency):
    if not _demo_available():
        return _blocked_response()
    summary = await DemoSeeder(session).seed_all()
    return success_response("DEMO_INSTALLED", data=summary.as_dict())


@router.get("/reset")
async def demo_reset(session: AsyncSessionDependency):
    if not _demo_available():
        return _blocked_response()
    summary = await DemoSeeder(session).reset()
    return success_response("DEMO_RESET", data=summary.as_dict())


@router.get("/scenarios")
async def demo_scenarios(session: AsyncSessionDependency):
    if not _demo_available():
        return _blocked_response()
    return success_response("DEMO_SCENARIOS_RETRIEVED", data=await DemoSeeder(session).scenarios())
