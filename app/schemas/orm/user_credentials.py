from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class UserCredentials(ORMSchema):
    password: str
