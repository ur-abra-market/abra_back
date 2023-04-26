from __future__ import annotations

from asyncio import run

from _core import setup

from orm.core.session import _engine  # noqa


async def main() -> None:
    _engine.echo = False

    await setup()


if __name__ == "__main__":
    run(main())
