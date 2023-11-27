from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from schemas.bundle_variation_pod_price import BundleVariationPodPrice

    from .bundle_product_variation_value import BundleProductVariationValue
    from .bundle_variation_pod_amount import BundleVariationPodAmount
    from .product import Product


class BundleVariationPod(ORMSchema):
    bundle_variation_pod_amount: Optional[BundleVariationPodAmount] = None
    bundle_variations: Optional[List[BundleProductVariationValue]] = None
    prices: Optional[List[BundleVariationPodPrice]] = None
    product: Optional[Product] = None
