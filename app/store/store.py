from .app import App
from .mail import Mail
from .orm import ORM


class Store:
    def __init__(self) -> None:
        self.app = App()
        self.mail = Mail()
        self.orm = ORM()
