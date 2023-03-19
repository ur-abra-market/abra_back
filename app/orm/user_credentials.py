from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class UserCredentialsModel(mixins.UserIDMixin, ORMModel):
    password: Mapped[str]
