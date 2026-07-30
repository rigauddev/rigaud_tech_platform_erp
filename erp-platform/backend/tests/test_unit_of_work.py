import pytest

from app.shared.infrastructure.unit_of_work import SQLAlchemyUnitOfWork


class FakeSession:
    def __init__(self) -> None:
        self.begin_called = False
        self.commit_called = False
        self.rollback_called = False
        self.close_called = False

    async def begin(self) -> None:
        self.begin_called = True

    async def commit(self) -> None:
        self.commit_called = True

    async def rollback(self) -> None:
        self.rollback_called = True

    async def close(self) -> None:
        self.close_called = True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unit_of_work_rolls_back_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_session = FakeSession()

    monkeypatch.setattr(
        "app.shared.infrastructure.unit_of_work.async_session_factory",
        lambda: fake_session,
    )

    with pytest.raises(RuntimeError):
        async with SQLAlchemyUnitOfWork():
            raise RuntimeError("boom")

    assert fake_session.begin_called is True
    assert fake_session.rollback_called is True
    assert fake_session.close_called is True
    assert fake_session.commit_called is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_unit_of_work_requires_explicit_commit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_session = FakeSession()

    monkeypatch.setattr(
        "app.shared.infrastructure.unit_of_work.async_session_factory",
        lambda: fake_session,
    )

    async with SQLAlchemyUnitOfWork() as unit_of_work:
        await unit_of_work.commit()

    assert fake_session.begin_called is True
    assert fake_session.commit_called is True
    assert fake_session.rollback_called is False
    assert fake_session.close_called is True
