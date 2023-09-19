from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle import Bundle
    from .bundle_variation_pod import BundleVariationPod


class BundleVariation(ORMSchema):
    variation_value_to_product_id: int
    bundle_id: int
    bundle_variation_pod_id: int

    bundle: Optional[Bundle] = None
    pod: Optional[BundleVariationPod] = None
