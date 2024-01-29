from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .bundle_upload import BundleUpload
from .product_pricing import ProductPricingUpload
from .property_value import PropertyValueUpload
from .variation_value import VariationValueUpload


class ProductAddUpload(ApplicationSchema):
    name: str
    description: str
    brand: int
    images: Optional[List[str]]

    category: Optional[int]

    properties: Optional[List[PropertyValueUpload]]

    product_variations: Optional[List[VariationValueUpload]]

    bundles: Optional[List[BundleUpload]]

    pricing: Optional[ProductPricingUpload]
