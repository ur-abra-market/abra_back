from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel
    from .product_review_photo import ProductReviewPhotoModel
    from .product_review_reaction import ProductReviewReactionModel


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[types.text]
    grade_overall: Mapped[types.small_int]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="reviews")
    photos: Mapped[List[ProductReviewPhotoModel]] = relationship(back_populates="review")
    reactions: Mapped[List[ProductReviewReactionModel]] = relationship(back_populates="review")
