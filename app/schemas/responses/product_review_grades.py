from __future__ import annotations

from typing import List, Optional

from ..schema import ApplicationSchema
from .product_review_details import ProductReviewDetails


class ProductReviewGrades(ApplicationSchema):
    grade_average: float
    review_count: int
    details: Optional[List[ProductReviewDetails]] = None
