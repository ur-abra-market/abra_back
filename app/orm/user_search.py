from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class UserSearchModel(mixins.UserIDMixin, ORMModel):
    search_query: Mapped[text]
    datetime: Mapped[datetime]
