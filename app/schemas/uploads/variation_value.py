from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .product_image import ProductImageUpload


class VariationValueUpload(ApplicationSchema):
    variation_values_id: int
    images: Optional[List[ProductImageUpload]] = None
