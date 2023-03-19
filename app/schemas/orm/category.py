from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category_property_type import CategoryPropertyType
    from app.schemas.orm.category_variation_type import CategoryVariationType
    from app.schemas.orm.product import Product


class Category(ORMSchema):
    name: str
    level: int
    parent_id: Optional[int] = None
    products: List[Product]
    properties: List[CategoryPropertyType]
    variations: List[CategoryVariationType]
