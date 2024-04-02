from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product_image import ProductImage
    from .supplier import Supplier


class ProductForReviews(ORMSchema):
    name: str
    images: Optional[List[ProductImage]]
    grade_average: float
    reviews_count: int
    supplier: Supplier
