from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from pydantic import UUID4

from .schema import ORMSchema

if TYPE_CHECKING:
    from .category import Category
    from .category_property_value import CategoryPropertyValue
    from .category_variation_value import CategoryVariationValue
    from .seller import Seller
    from .supplier import Supplier
    from .tags import Tags


class Product(ORMSchema):
    category_id: int
    supplier_id: int
    name: str
    description: Optional[str] = None
    datetime: datetime
    grade_average: float = 0.0
    total_orders: int = 0
    uuid: UUID4
    is_active: bool = True
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None
    tags: Optional[List[Tags]] = None
    properties: Optional[List[CategoryPropertyValue]] = None
    variations: Optional[List[CategoryVariationValue]] = None
    favorites_by_users: Optional[List[Seller]] = None
