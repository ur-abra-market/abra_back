from __future__ import annotations

from .token import TokenAccessor


class App:
    def __init__(self) -> None:
        self.token = TokenAccessor()
