# mypy: disable-error-code="no-redef"

from __future__ import annotations

from typing import Final

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.settings import database_settings

POOL_RECYCLE: Final[int] = 60 * 5  # 300


def engine(echo: bool) -> AsyncEngine:
    return create_async_engine(
        database_settings.url,
        pool_recycle=POOL_RECYCLE,
        pool_size=15,
        max_overflow=30,
        pool_pre_ping=True,
        isolation_level="SERIALIZABLE",
        echo=echo,
    )


def get_async_sessionmaker(echo: bool):
    return sessionmaker(
        bind=engine(echo=echo),
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
