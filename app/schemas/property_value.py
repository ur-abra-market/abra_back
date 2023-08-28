from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .property_type import PropertyType


class PropertyValue(ORMSchema):
    value: str
    optional_value: Optional[str]
    property_type_id: int
    type: Optional[PropertyType] = None
    products: Optional[List[Product]] = None
