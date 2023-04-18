from __future__ import annotations

from .core import ORMSchema


class OrderProductVariation(ORMSchema):
    count: int
    product_variation_count_id: int
