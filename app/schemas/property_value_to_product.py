from __future__ import annotations

from typing import Optional

from .core import ORMSchema


class PropertyValueToProduct(ORMSchema):
    property_value_id: int
    product_id: int
    optional_value: Optional[str]
