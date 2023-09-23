from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .property_type import PropertyType
    from .variation_type import VariationType


class Category(ORMSchema):
    name: str
    level: int
    parent_id: Optional[int] = None
    children: Optional[List[Category]] = None
    products: Optional[List[Product]] = None
    properties: Optional[List[PropertyType]] = None
    variations: Optional[List[VariationType]] = None