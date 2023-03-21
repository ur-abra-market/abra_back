from __future__ import annotations

from .schema import ORMSchema


class ProductVariationValue(ORMSchema):
    product_id: int
    variation_value_id: int
