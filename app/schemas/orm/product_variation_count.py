from __future__ import annotations

from .core import ORMSchema


class ProductVariationCount(ORMSchema):
    count: int
