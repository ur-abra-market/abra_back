from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, str_16, str_30


class UserPaymentCredentialsModel(mixins.UserIDMixin, ORMModel):
    card_holder: Mapped[str_30]
    card_number: Mapped[str_16]
    expired_date: Mapped[str_30]
