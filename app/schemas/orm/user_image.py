from __future__ import annotations

from typing import Optional

from .schema import ORMSchema


class UserImage(ORMSchema):
    user_id: int
    source_url: Optional[str] = None
