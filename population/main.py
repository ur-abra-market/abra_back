from __future__ import annotations

from asyncio import run

from loaders import setup
from utils.database import remove_data
from utils.time import exec_time


@exec_time(title="Population")
async def main() -> None:
    await remove_data()
    await setup()


if __name__ == "__main__":
    run(main())
