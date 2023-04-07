from __future__ import annotations

import datetime as dt

from .schema import ORMSchema


class UserSearch(ORMSchema):
    user_id: int
    search_query: str
    datetime: dt.datetime
