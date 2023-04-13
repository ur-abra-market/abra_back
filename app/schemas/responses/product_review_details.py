from __future__ import annotations

from ..schema import ApplicationSchema


class ProductReviewDetails(ApplicationSchema):
    grade_overall: int = 0
    review_count: int = 0
