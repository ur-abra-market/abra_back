from __future__ import annotations

from typing import Optional

from pydantic import Field

from enums import ProductFilterValuesEnum

from ..schema import ApplicationSchema
from .product_price_range import ProductPriceRangeUpload


class SupplierFilterProductListUpload(ApplicationSchema):
    category_ids: Optional[list[int]]
    on_sale: Optional[ProductFilterValuesEnum]
    is_active: Optional[ProductFilterValuesEnum]
    query: Optional[str] = Field("", min_length=0)
    price_range: Optional[ProductPriceRangeUpload]
