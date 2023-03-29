from typing import List, Optional, TYPE_CHECKING

from ..schema import ApplicationSchema

if TYPE_CHECKING:
    from .product_review_details import ProductReviewDetails


class ProductReviewGrades(ApplicationSchema):
    grade_average: float = 0
    review_count: int = 0
    details: Optional[List[ProductReviewDetails]] = None
