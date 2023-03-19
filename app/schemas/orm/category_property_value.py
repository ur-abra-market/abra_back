from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category_property_type import CategoryPropertyType
    from app.schemas.orm.product import Product


class CategoryPropertyValue(ORMSchema):
    value: str
    optional_value: Optional[str] = None
    property_type_id: int
    type: Optional[CategoryPropertyType] = None
    products: List[Product]
