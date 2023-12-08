from __future__ import annotations

from typing import List, Optional

from enums import ProductFilterValuesEnum

from ..schema import ApplicationSchema
from .product_price_range import ProductPriceRangeUpload
from .product_property import ProductPropertyUpload


class ProductListFiltersUpload(ApplicationSchema):
    category_ids: Optional[List[int]]
    on_sale: Optional[ProductFilterValuesEnum] = ProductFilterValuesEnum.ALL
    query: Optional[str]
    price_range: Optional[ProductPriceRangeUpload]
    brand: Optional[List[int]]
    property: Optional[ProductPropertyUpload]
