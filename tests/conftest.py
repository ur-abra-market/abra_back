from __future__ import annotations

import asyncio

import pytest
from fastapi import FastAPI
from fastapi_jwt_auth import AuthJWT
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import Settings
from population import setup as setup_population


@pytest.fixture(scope="session")
def event_loop() -> asyncio.BaseEventLoop:
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True, scope="session")
async def populate() -> None:
    from orm.core import ORMModel, engine

    engine.echo = False

    async with engine.begin() as connection:
        await connection.run_sync(ORMModel.metadata.drop_all)
        await connection.run_sync(ORMModel.metadata.create_all)

    await setup_population()


@pytest.fixture(scope="function")
async def session() -> AsyncSession:
    from orm.core.session import async_sessionmaker

    async with async_sessionmaker.begin() as _session:
        yield _session


@pytest.fixture(scope="session")
def app() -> FastAPI:
    from app import create_application

    _app = create_application()

    def get_config() -> Settings:
        settings = Settings()
        settings.authjwt_cookie_domain = None

        return settings

    AuthJWT.load_config(get_config)

    yield _app
