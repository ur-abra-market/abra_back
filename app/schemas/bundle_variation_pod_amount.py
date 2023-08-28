from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .order import Order


class BundleVariationPodAmount(ORMSchema):
    bundle_variation_pod_id: int
    amount: int

    products: Optional[Order] = None
