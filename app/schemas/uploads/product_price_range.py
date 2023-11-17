from __future__ import annotations

from ..schema import ApplicationSchema


class ProductPriceRangeUpload(ApplicationSchema):
    min_price: int
    max_price: int
