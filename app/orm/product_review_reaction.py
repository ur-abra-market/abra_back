from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .product_review import ProductReviewModel
    from .seller import SellerModel


class ProductReviewReactionModel(mixins.ProductReviewIDMixin, mixins.SellerIDMixin, ORMModel):
    reaction: Mapped[bool]

    review: Mapped[Optional[ProductReviewModel]] = relationship(back_populates="reactions")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="review_reactions")
