from typing import List, Optional

from pydantic import HttpUrl

from ...schema import ApplicationSchema


class ProductReview(ApplicationSchema):
    product_review_photo: Optional[List[HttpUrl]] = None
    product_review_text: str
    product_review_grade: int
