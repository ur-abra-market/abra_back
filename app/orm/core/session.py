# mypy: disable-error-code="no-redef"

from __future__ import annotations

from typing import Final

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import database_settings, fastapi_uvicorn_settings

POOL_RECYCLE: Final[int] = 60 * 5  # 300


def engine(echo: bool = fastapi_uvicorn_settings.DEBUG) -> AsyncEngine:
    return create_async_engine(
        database_settings.url,
        pool_recycle=POOL_RECYCLE,
        isolation_level="SERIALIZABLE",
        echo=echo,
    )


def async_sessionmaker(echo: bool = None) -> AsyncSession:
    return sessionmaker(  # type: ignore[call-overload]
        bind=engine(echo=echo),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
