from __future__ import annotations

import datetime as dt

from .core import ORMSchema, mixins


class UserSearch(mixins.UserIDMixin, ORMSchema):
    search_query: str
    datetime: dt.datetime
