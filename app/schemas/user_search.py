from __future__ import annotations

import datetime as dt

from .core import ORMSchema


class UserSearch(ORMSchema):
    search_query: str
