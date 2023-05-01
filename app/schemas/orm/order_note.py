from __future__ import annotations

from .core import ORMSchema


class OrderNote(ORMSchema):
    text: str
