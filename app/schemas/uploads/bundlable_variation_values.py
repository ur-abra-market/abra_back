from __future__ import annotations

from ..schema import ApplicationSchema


class BundlableVariationValueUpload(ApplicationSchema):
    variation_type_id: int
    variation_value_id: int
    bundle_id: int
    amount: int
