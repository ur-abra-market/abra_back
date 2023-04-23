from __future__ import annotations

from asyncio import run
from contextlib import suppress

from _core import setup
from sqlalchemy.exc import SQLAlchemyError

from orm.core.session import _engine  # noqa


async def main() -> None:
    _engine.echo = False

    with suppress(SQLAlchemyError):
        await setup()


if __name__ == "__main__":
    run(main())
