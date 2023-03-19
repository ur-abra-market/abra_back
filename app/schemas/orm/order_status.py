from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class OrderStatus(ORMSchema):
    name: str
