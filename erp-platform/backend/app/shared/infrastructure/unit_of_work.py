from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_factory


class SQLAlchemyUnitOfWork:
    """Async Unit of Work for application-layer transaction boundaries."""

    def __init__(self) -> None:
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> Self:
        self.session = async_session_factory()
        await self.begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.rollback()
        finally:
            await self.session.close()

    async def begin(self) -> None:
        if self.session is None:
            self.session = async_session_factory()
        await self.session.begin()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work session is not initialized.")
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError("Unit of Work session is not initialized.")
        await self.session.rollback()
