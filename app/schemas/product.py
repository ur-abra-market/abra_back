from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from pydantic import UUID4

from .core import ORMSchema

if TYPE_CHECKING:
    from .category import Category
    from .product_image import ProductImage

    # from .product_price import ProductPrice
    from .product_review import ProductReview
    from .property_value import PropertyValue
    from .seller import Seller
    from .supplier import Supplier
    from .tags import Tags
    from .variation_value import VariationValue


class Product(ORMSchema):
    name: str
    description: Optional[str] = None
    datetime: dt.datetime
    grade_average: float = 0.0
    total_orders: int = 0
    uuid: UUID4
    is_active: bool = True
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None
    images: Optional[List[ProductImage]] = None
    tags: Optional[List[Tags]] = None
    # prices: Optional[List[ProductPrice]] = None
    properties: Optional[List[PropertyValue]] = None
    variations: Optional[List[VariationValue]] = None
    favorites_by_users: Optional[List[Seller]] = None
    reviews: Optional[List[ProductReview]] = None
