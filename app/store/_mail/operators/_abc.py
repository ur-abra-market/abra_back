import abc
from typing import Any

from .._interface import MailInterface

SUBTYPE = "html"


class MailABC(abc.ABC):
    TEMPLATE: str

    def __init__(
        self, interface: MailInterface
    ) -> None:
        self.interface = interface

    @abc.abstractmethod
    def _format_template(self, *args: Any, **kwargs: Any) -> str:
        ...

    async def send(
        self, *args: Any, **kwargs: Any
    ) -> None:
        await self._send(*args, **kwargs)

    @abc.abstractmethod
    async def _send(self, *args: Any, **kwargs: Any) -> None:
        ...
