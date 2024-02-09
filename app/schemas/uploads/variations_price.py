from __future__ import annotations

from datetime import datetime

from ..schema import ApplicationSchema


class VariationPriceUpload(ApplicationSchema):
    variation_value_id: int
    discount: float
    related_to_base_price: float
    min_quantity: int
    start_date: datetime
    end_date: datetime
