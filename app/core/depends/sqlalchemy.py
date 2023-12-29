from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from core.settings import fastapi_uvicorn_settings
from orm.core import get_async_sessionmaker

async_sessionmaker = get_async_sessionmaker(echo=fastapi_uvicorn_settings.DEBUG)


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async with async_sessionmaker() as session:
        yield session
