from ._interface import MailInterface
from .operators import MailConfirm


class Mail:
    def __init__(self) -> None:
        self._interface = MailInterface()
        self.confirm = MailConfirm(self._interface)
