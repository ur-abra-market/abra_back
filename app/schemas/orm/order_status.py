from __future__ import annotations

from .core import ORMSchema


class OrderStatus(ORMSchema):
    name: str
