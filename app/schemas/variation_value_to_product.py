from __future__ import annotations

from .core import ORMSchema


class VariationValueToProduct(ORMSchema):
    variation_value_id: int
    product_id: int
