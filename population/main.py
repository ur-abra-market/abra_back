from __future__ import annotations

from asyncio import run

from _core import setup

from orm.core import ORMModel
from orm.core.session import _engine  # noqa


async def main() -> None:
    _engine.echo = False
    async with _engine.begin() as s:
        await s.run_sync(ORMModel.metadata.drop_all)
        await s.run_sync(ORMModel.metadata.create_all)
    _engine.echo = False

    await setup()


if __name__ == "__main__":
    run(main())
