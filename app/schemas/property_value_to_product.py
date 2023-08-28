from __future__ import annotations

from .core import ORMSchema


class PropertyValueToProduct(ORMSchema):
    property_value_id: int
    product_id: int
