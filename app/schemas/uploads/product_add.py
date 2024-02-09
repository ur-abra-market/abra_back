from __future__ import annotations

from typing import Dict, List, Optional

from ..schema import ApplicationSchema
from .bundle_upload import BundleUpload
from .product_pricing import ProductPriceUpload
from .property_value import PropertyValueUpload
from .variation_value import VariationValueUpload


class ProductAddUpload(ApplicationSchema):
    name: str
    description: str
    brand: int
    images: Optional[Dict[int, str]] = None

    category: Optional[int]

    properties: Optional[List[PropertyValueUpload]]

    variations: Optional[List[VariationValueUpload]]

    bundles: Optional[List[BundleUpload]]

    prices: Optional[ProductPriceUpload]
