from __future__ import annotations

from .pwd import PWDAccessor
from .token import TokenAccessor


class App:
    def __init__(self) -> None:
        self.pwd = PWDAccessor()
        self.token = TokenAccessor()
