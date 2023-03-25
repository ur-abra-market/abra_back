from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import database_settings

POOL_RECYCLE = 60 * 5  # 300

_engine = create_async_engine(database_settings.url, pool_recycle=POOL_RECYCLE)
async_sessionmaker = sessionmaker(
    bind=_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)
