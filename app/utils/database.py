from __future__ import annotations

from logger import logger
from orm.core import ORMModel, async_sessionmaker
from utils.time import exec_time


@exec_time(title="Removing data")
async def remove_data() -> None:
    logger.info("Removing data from tables..")
    async with async_sessionmaker(echo=False).begin() as session:
        for table in reversed(ORMModel.metadata.sorted_tables):
            await session.execute(table.delete())
