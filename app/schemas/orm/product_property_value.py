from __future__ import annotations

from .schema import ORMSchema


class ProductPropertyValue(ORMSchema):
    product_id: int
    property_value_id: int
