from typing import List, Optional

from ...schema import ApplicationSchema
from .product_price import ProductPrice


class ProductUpload(ApplicationSchema):
    name: str
    category_id: int
    property_ids: Optional[List[int]] = []
    varitaion_ids: Optional[List[int]] = []
    description: Optional[str]
    grade_average: Optional[float] = 0.0
    prices: List[ProductPrice]
