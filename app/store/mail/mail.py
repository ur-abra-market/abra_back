from __future__ import annotations

from .interface import MailInterface
from .operators import MailConfirm, MailForgot


class Mail:
    _interface = MailInterface()

    def __init__(self) -> None:
        self.confirm = MailConfirm(self._interface)
        self.forgot = MailForgot(self._interface)
