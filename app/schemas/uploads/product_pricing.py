from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from ..schema import ApplicationSchema
from .variations_price import VariationPriceUpload


class ProductPriceUpload(ApplicationSchema):
    product_base_price: float
    discount: float
    min_quantity: int
    start_date: datetime
    end_date: Optional[datetime]
    variations_price: Optional[List[VariationPriceUpload]]
