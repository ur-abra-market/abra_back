from .app import App
from .orm import ORM


class Store:
    def __init__(self) -> None:
        self.app = App()
        self.orm = ORM()
