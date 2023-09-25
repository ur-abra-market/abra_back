from __future__ import annotations

from ..schema import ApplicationSchema


class BundlableVariationValueUpload(ApplicationSchema):
    variation_value_to_product_id: int
    amount: int
