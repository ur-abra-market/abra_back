from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ...schema import ApplicationSchema

if TYPE_CHECKING:
    from ...orm import ProductPrice


class ProductUpload(ApplicationSchema):
    name: str
    category_id: int
    property_ids: Optional[List[int]] = None
    varitaion_ids: Optional[List[int]] = None
    description: Optional[str] = None
    grade_average: Optional[float] = 0.0
    prices: List[ProductPrice]
