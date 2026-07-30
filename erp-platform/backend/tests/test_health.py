import pytest
from httpx import ASGITransport, AsyncClient

from app.api.v1.routes import health
from app.main import create_app


@pytest.mark.asyncio
async def test_health_check() -> None:
    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_database_health_check(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_check_database_connection() -> bool:
        return True

    monkeypatch.setattr(health, "check_database_connection", fake_check_database_connection)

    app = create_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/health/database")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "reachable"}
