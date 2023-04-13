from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from ..schema import ApplicationSchema

if TYPE_CHECKING:
    from .product_review_details import ProductReviewDetails


class ProductReviewGrades(ApplicationSchema):
    grade_average: float = 0
    review_count: int = 0
    details: Optional[List[ProductReviewDetails]] = []
