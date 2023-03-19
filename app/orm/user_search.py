from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class UserSearchModel(mixins.UserIDMixin, ORMModel):
    search_query: Mapped[str]
    datetime: Mapped[datetime]
