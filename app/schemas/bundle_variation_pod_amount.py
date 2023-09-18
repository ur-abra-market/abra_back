from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .bundle_variation_pod import BundleVariationPod
    from .order import Order


class BundleVariationPodAmount(ORMSchema):
    bundle_variation_pod_id: int
    order_id: int
    amount: int

    order: Optional[Order] = None
    bundle_variation_pod: Optional[BundleVariationPod] = None
