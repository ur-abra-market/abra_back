from __future__ import annotations

from typing import Dict, List, Optional

from ..schema import ApplicationSchema
from .bundle_upload import BundleUpload
from .product_pricing import ProductPriceUpload
from .property_value import PropertyValueUpload
from .variation_value import VariationValueUpload


class ProductUpload(ApplicationSchema):
    name: str
    description: str
    brand: int
    category: Optional[int]
    images: Optional[Dict[int, str]]
    properties: Optional[List[PropertyValueUpload]]
    variations: Optional[List[VariationValueUpload]]
    bundles: Optional[List[BundleUpload]]
    prices: Optional[ProductPriceUpload]
