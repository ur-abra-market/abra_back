from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .schema import ORMSchema

if TYPE_CHECKING:
    from .category_variation_type import CategoryVariationType
    from .product import Product


class CategoryVariationValue(ORMSchema):
    variation_type_id: int
    value: str
    type: Optional[CategoryVariationType] = None
    products: Optional[List[Product]] = None
