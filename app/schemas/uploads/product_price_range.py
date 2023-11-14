from __future__ import annotations

from ..schema import ApplicationSchema


class ProductPriceRangeUpload(ApplicationSchema):
    min_price: int = 0
    max_price: int = 100_000
