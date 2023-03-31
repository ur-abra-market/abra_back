from ._base import BaseStore
from .app import App
from .mail import Mail
from .orm import ORM


class Store(BaseStore):
    def __init__(self) -> None:
        self.app = App()
        self.mail = Mail()
        self.orm = ORM()

    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...
