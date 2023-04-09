from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .category_property_type import CategoryPropertyType
    from .category_variation_type import CategoryVariationType
    from .product import Product


class Category(ORMSchema):
    name: str
    level: int
    parent_id: Optional[int] = None
    childs: Optional[List[Category]] = None
    products: Optional[List[Product]] = None
    properties: Optional[List[CategoryPropertyType]] = None
    variations: Optional[List[CategoryVariationType]] = None
