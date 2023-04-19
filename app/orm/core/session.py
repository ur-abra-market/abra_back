# mypy: disable-error-code="no-redef"
from __future__ import annotations

from typing import Final

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import database_settings, fastapi_settings  # noqa

POOL_RECYCLE: Final[int] = 60 * 5  # 300

_engine = create_async_engine(
    database_settings.url,
    pool_recycle=POOL_RECYCLE,
    isolation_level="SERIALIZABLE",
    echo=fastapi_settings.DEBUG,
)
async_sessionmaker = sessionmaker(
    bind=_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
