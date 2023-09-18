from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle_variation import BundleVariation
    from .bundle_variation_pod_amount import BundleVariationPodAmount
    from bundle_pod_price import BundlePodPrice


class BundleVariationPod(ORMSchema):
    bundle_variation_pod_amount: Optional[BundleVariationPodAmount] = None
    bundle_variations: Optional[List[BundleVariation]] = None
    prices: Optional[List[BundlePodPrice]] = None

