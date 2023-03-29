from typing import List, Optional

from ..schema import ApplicationSchema


class ProductReviewDetails(ApplicationSchema):
    grade_overall: int = 0
    count: int = 0