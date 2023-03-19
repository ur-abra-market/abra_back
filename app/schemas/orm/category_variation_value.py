from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category_variation_type import CategoryVariationType
    from app.schemas.orm.product import Product


class CategoryVariationValue(ORMSchema):
    variation_type_id: int
    value: str
    type: Optional[CategoryVariationType] = None
    products: List[Product]
