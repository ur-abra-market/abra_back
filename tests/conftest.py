from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(scope="session")
def event_loop() -> asyncio.BaseEventLoop:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def run_migrations() -> None:
    from orm.core import ORMModel
    from orm.core.session import _engine  # noqa

    _engine.echo = False

    async with _engine.begin() as connection:
        await connection.run_sync(ORMModel.metadata.drop_all)
        await connection.run_sync(ORMModel.metadata.create_all)


@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    from orm.core.session import async_sessionmaker

    async with async_sessionmaker.begin() as _session:
        yield _session


@pytest.fixture(autouse=True, scope="session")
def settings_changer() -> None:
    from core.settings import fastapi_settings

    fastapi_settings.DEBUG = True


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from app import app as _app

    yield _app
