from __future__ import annotations

from typing import List, Optional

from pydantic import Field

from enums import ProductFilterValuesEnum

from ..schema import ApplicationSchema
from .product_price_range import ProductPriceRangeUpload


class ProductListFiltersUpload(ApplicationSchema):
    category_ids: Optional[List[int]]
    on_sale: Optional[ProductFilterValuesEnum] = ProductFilterValuesEnum.ALL
    query: Optional[str] = Field("", min_length=0)
    price_range: Optional[ProductPriceRangeUpload]
