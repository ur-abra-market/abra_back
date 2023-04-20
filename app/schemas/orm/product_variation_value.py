from __future__ import annotations

from .core import ORMSchema


class ProductVariationValue(ORMSchema):
    variation_value_id: int
    product_id: int
