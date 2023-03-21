from .pwd import PWDAccessor


class App:
    def __init__(self) -> None:
        self.pwd = PWDAccessor()
