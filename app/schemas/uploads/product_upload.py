from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema


class ProductUpload(ApplicationSchema):
    category_id: int
    name: str
    description: Optional[str] = None
    properties: Optional[List[int]] = None
    brand_id: int
    variations: Optional[List[int]] = None
    grade_average: Optional[float] = 0.0
