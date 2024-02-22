from __future__ import annotations

from logger import logger
from orm.core import ORMModel, engine
from utils.time import exec_time


@exec_time(title="Removing data")
async def remove_data() -> None:
    logger.info("Removing data from tables..")
    async with engine(echo=False).begin() as session:
        await session.run_sync(ORMModel.metadata.drop_all)
        await session.run_sync(ORMModel.metadata.create_all)
        # for table in reversed(ORMModel.metadata.sorted_tables):
        #     await session.execute(table.delete())
