from __future__ import annotations

from ..schema import ApplicationSchema


class BundlableVariationValueUpload(ApplicationSchema):
    variation_value_id: int
    amount: int
