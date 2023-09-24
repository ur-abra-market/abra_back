from __future__ import annotations

from typing import Dict, List, Optional

from ..schema import ApplicationSchema
from .bundlable_variation_values import BundlableVariationValueUpload


class ProductUpload(ApplicationSchema):
    name: str
    category_id: int
    properties: Optional[List[int]] = None
    variations: Optional[List[int]] = None
    bundlable_variation_values: List[BundlableVariationValueUpload] = None
    description: Optional[str] = None
    grade_average: Optional[float] = 0.0
    stock: int
