from .app import App
from ._mail import Mail
from .orm import ORM
from .s3 import AWSS3
from ._base import BaseStore


class Store(BaseStore):
    def __init__(self) -> None:
        self.app = App()
        self.mail = Mail()
        self.orm = ORM()
        self.aws_s3 = AWSS3()

    async def connect(self) -> None:
        await self.aws_s3.connect()

    async def disconnect(self) -> None:
        await self.aws_s3.disconnect()
