from __future__ import annotations

from typing import List, Optional

from .product_price_upload import ProductPriceUpload
from .schema import ApplicationSchema


class ProductUpload(ApplicationSchema):
    name: str
    category_id: int
    properties: Optional[List[int]] = None
    variations: Optional[List[int]] = None
    description: Optional[str] = None
    grade_average: Optional[float] = 0.0
    prices: List[ProductPriceUpload]