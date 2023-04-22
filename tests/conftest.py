from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app import create_application
from core.depends import get_session
from orm.core.session import _engine, async_sessionmaker  # noqa


@pytest.fixture(scope="session")
def event_loop() -> asyncio.BaseEventLoop:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
def run_migrations() -> None:
    import os

    os.system("alembic upgrade head")


@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    async with async_sessionmaker.begin() as _session:
        yield _session


@pytest.fixture(scope="session")
def app() -> FastAPI:
    _app = create_application()

    async def _get_session() -> AsyncSession:
        async with async_sessionmaker.begin() as _session:
            yield _session

    _app.dependency_overrides[get_session] = _get_session

    yield _app
