from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .bundles_price import BundlesPriceUpload
from .variations_price import VariationPricingUpload


class ProductPricingUpload(ApplicationSchema):
    product_base_price: float
    variations_pricing: Optional[List[VariationPricingUpload]]
    bundles_pricing: Optional[List[BundlesPriceUpload]]
