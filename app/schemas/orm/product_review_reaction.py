from __future__ import annotations

from .schema import ORMSchema


class ProductReviewReaction(ORMSchema):
    product_review_id: int
    seller_id: int
    reaction: bool
