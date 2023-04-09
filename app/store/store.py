from __future__ import annotations

from loguru import logger

from .aws_s3 import AWSS3
from .orm import ORM


class Store:
    def __init__(self) -> None:
        self.aws_s3 = AWSS3()
        self.orm = ORM()

    async def connect(self) -> None:  # noqa
        logger.info("Initialize tools")

    async def disconnect(self) -> None:  # noqa
        logger.info("Cleanup tools")
