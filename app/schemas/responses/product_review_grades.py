from typing import List, Optional

from ..schema import ApplicationSchema
from .product_review_details import ProductReviewDetails


class ProductReviewGrades(ApplicationSchema):
    grade_average: float = 0
    review_count: int = 0
    details: Optional[List[ProductReviewDetails]] = []
