from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class Admin(ORMSchema):
    user_id: int
