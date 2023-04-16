from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .product_review import ProductReview
    from .seller import Seller


class ProductReviewReaction(ORMSchema):
    reaction: bool
    review: Optional[ProductReview] = None
    seller: Optional[Seller] = None
