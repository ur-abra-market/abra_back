from __future__ import annotations

from orm.core import engine, ORMModel


async def migrations() -> None:
    engine.echo = False

    async with engine.begin() as connection:
        await connection.run_sync(ORMModel.metadata.drop_all)
        await connection.run_sync(ORMModel.metadata.create_all)
