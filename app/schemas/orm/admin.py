from __future__ import annotations

from .schema import ORMSchema


class Admin(ORMSchema):
    user_id: int
