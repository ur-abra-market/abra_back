from __future__ import annotations

from ..schema import ApplicationSchema


class ProductReviewDetails(ApplicationSchema):
    grade_overall: int
    review_count: int
