import pytest
from sqlalchemy import text

from app.core.config import settings
from app.database.session import async_engine, async_session_factory, check_database_connection


@pytest.mark.integration
def test_integration_database_is_not_production() -> None:
    assert settings.app_env != "production"
    assert "prod" not in settings.database_url.lower()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_database_connection_executes_select_one() -> None:
    assert await check_database_connection() is True


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_session_executes_query() -> None:
    async with async_session_factory() as session:
        result = await session.execute(text("select 1"))

    assert result.scalar_one() == 1


@pytest.mark.integration
@pytest.mark.asyncio
async def test_async_engine_uses_postgresql_dialect() -> None:
    assert async_engine.dialect.name == "postgresql"
