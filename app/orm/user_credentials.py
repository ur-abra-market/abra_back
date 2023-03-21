from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class UserCredentialsModel(mixins.UserIDMixin, ORMModel):
    password: Mapped[text]
