from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class UserSearchModel(mixins.UserIDMixin, ORMModel):
    search_query: Mapped[types.text]
