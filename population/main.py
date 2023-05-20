from __future__ import annotations

from asyncio import run

from loaders import setup
from orm.core import ORMModel, engine


async def main() -> None:
    engine.echo = False

    async with engine.begin() as connection:
        await connection.run_sync(ORMModel.metadata.drop_all)
        await connection.run_sync(ORMModel.metadata.create_all)

    await setup()


if __name__ == "__main__":
    run(main())
