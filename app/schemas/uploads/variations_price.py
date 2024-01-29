from __future__ import annotations

from ..schema import ApplicationSchema


class VariationPricingUpload(ApplicationSchema):
    variation_value_id: int
    discount: float
    related_to_base_price: float
