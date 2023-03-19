from __future__ import annotations

from datetime import datetime

from app.schemas.orm.schema import ORMSchema


class UserSearch(ORMSchema):
    user_id: int
    search_query: str
    datetime: datetime
