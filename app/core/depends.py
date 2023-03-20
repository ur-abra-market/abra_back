from sqlalchemy.ext.asyncio import AsyncSession

from app.orm.core import async_sessionmaker


async def get_session() -> AsyncSession:
    async with async_sessionmaker.begin() as _session:
        yield _session
