from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema

# from .product_price import ProductPriceUpload


class ProductEditUpload(ApplicationSchema):
    name: Optional[str]
    category_id: Optional[int]
    properties: Optional[List[int]] = None
    variations: Optional[List[int]] = None
    description: Optional[str] = None
    grade_average: Optional[float] = 0.0
    # prices: Optional[List[ProductPriceUpload]] = None
