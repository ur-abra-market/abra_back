from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app import create_application
from app.orm.core.session import _engine, async_sessionmaker  # noqa
from core.depends import get_session


@pytest.fixture(scope="session")
def event_loop() -> asyncio.BaseEventLoop:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def database() -> None:
    _engine.echo = False


@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    async with async_sessionmaker.begin() as _session:
        yield _session
        await _session.rollback()


@pytest.fixture(scope="session")
def app() -> FastAPI:
    _app = create_application()

    async def _get_session() -> AsyncSession:
        async with async_sessionmaker.begin() as _session:
            yield _session
            await _session.rollback()

    _app.dependency_overrides[get_session] = _get_session

    yield _app
