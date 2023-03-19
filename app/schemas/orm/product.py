from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from datetime import datetime

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.category import Category
    from app.schemas.orm.category_property_value import CategoryPropertyValue
    from app.schemas.orm.category_variation_value import CategoryVariationValue
    from app.schemas.orm.seller import Seller
    from app.schemas.orm.supplier import Supplier
    from app.schemas.orm.tags import Tags


class Product(ORMSchema):
    category_id: int
    supplier_id: int
    name: str
    description: Optional[str] = None
    datetime: datetime
    grade_average: float = 0.0
    total_orders: int = 0
    uuid: str
    is_active: bool = True
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None
    tags: List[Tags]
    properties: List[CategoryPropertyValue]
    variations: List[CategoryVariationValue]
    favorites_by_users: List[Seller]
