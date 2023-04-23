from .csv_loader import csv_loader
from .generator import generator


async def setup() -> None:
    await csv_loader.setup()
    await generator.setup()


__all__ = ("setup",)
