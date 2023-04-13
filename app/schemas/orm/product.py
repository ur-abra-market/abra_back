from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from pydantic import UUID4

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .category import Category
    from .category_property_value import CategoryPropertyValue
    from .category_variation_value import CategoryVariationValue
    from .product_image import ProductImage
    from .product_price import ProductPrice
    from .product_review import ProductReview
    from .seller import Seller
    from .supplier import Supplier
    from .tags import Tags


class Product(mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMSchema):
    name: str
    description: Optional[str] = None
    datetime: dt.datetime
    grade_average: float = 0.0
    total_orders: int = 0
    uuid: UUID4
    is_active: bool = True
    category: Optional[Category] = None
    supplier: Optional[Supplier] = None
    tags: Optional[List[Tags]] = None
    prices: Optional[List[ProductPrice]] = None
    properties: Optional[List[CategoryPropertyValue]] = None
    variations: Optional[List[CategoryVariationValue]] = None
    favorites_by_users: Optional[List[Seller]] = None
    reviews: Optional[List[ProductReview]] = None
    images: Optional[List[ProductImage]] = None
