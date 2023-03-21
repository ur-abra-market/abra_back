from __future__ import annotations

from typing import Optional

from .schema import ORMSchema


class UserImage(ORMSchema):
    user_id: int
    thumbnail_url: Optional[str] = None
    source_url: Optional[str] = None
