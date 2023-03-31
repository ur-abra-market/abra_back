from .app import App
from .aws_s3 import AWSS3
from .base import BaseStore
from .mail import Mail
from .orm import ORM


class Store(BaseStore):
    def __init__(self) -> None:
        self.app = App()
        self.aws_s3 = AWSS3()
        self.mail = Mail()
        self.orm = ORM()

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...
