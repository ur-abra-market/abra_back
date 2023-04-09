from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .category_property_type import CategoryPropertyType
    from .product import Product


class CategoryPropertyValue(ORMSchema):
    value: str
    optional_value: Optional[str] = None
    property_type_id: int
    type: Optional[CategoryPropertyType] = None
    products: Optional[List[Product]] = None
