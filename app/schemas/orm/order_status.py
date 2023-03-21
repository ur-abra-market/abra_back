from __future__ import annotations

from .schema import ORMSchema


class OrderStatus(ORMSchema):
    name: str
