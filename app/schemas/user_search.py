from __future__ import annotations

from .core import ORMSchema


class UserSearch(ORMSchema):
    search_query: str
