from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .product_image import ProductImage


class ProductImages(ApplicationSchema):
    images: Optional[List[ProductImage]] = []
