from __future__ import annotations

from typing import TYPE_CHECKING, List

from ..schema import ApplicationSchema

if TYPE_CHECKING:
    from .bundlable_variation_values import BundlableVariationValueUpload


class BundleUpload(ApplicationSchema):
    name: str
    variation_type_id: int
    bundlable_variation_values: List[BundlableVariationValueUpload]
