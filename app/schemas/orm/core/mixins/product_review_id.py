from __future__ import annotations

from pydantic import BaseModel


class ProductReviewIDMixin(BaseModel):
    product_review_id: int
