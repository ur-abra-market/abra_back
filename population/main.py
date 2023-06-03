from __future__ import annotations

from asyncio import run

from loaders import setup
from utils.migrations import migrations


async def main() -> None:
    await migrations()
    await setup()


if __name__ == "__main__":
    run(main())
