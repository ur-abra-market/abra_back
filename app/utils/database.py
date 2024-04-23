from __future__ import annotations

from logger import logger
from orm.core import ORMModel, engine, get_async_sessionmaker
from utils.time import exec_time


@exec_time(title="Removing data")
async def remove_data() -> None:
    logger.info("Removing data from tables..")
    async with get_async_sessionmaker(echo=False).begin() as session:
        for table in reversed(ORMModel.metadata.sorted_tables):
            await session.execute(table.delete())


@exec_time(title="Removing data")
async def migrations() -> None:
    engine.echo = False

    async with engine(echo=False).begin() as connection:
        await connection.run_sync(ORMModel.metadata.drop_all)
        await connection.run_sync(ORMModel.metadata.create_all)
