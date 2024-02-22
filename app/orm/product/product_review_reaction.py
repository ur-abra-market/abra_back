from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from orm.core import ORMModel, mixins, types

if TYPE_CHECKING:
    from orm.seller import SellerModel

    from .product_review import ProductReviewModel


class ProductReviewReactionModel(mixins.ProductReviewIDMixin, mixins.SellerIDMixin, ORMModel):
    reaction: Mapped[types.bool_no_value]

    review: Mapped[Optional[ProductReviewModel]] = relationship(back_populates="reactions")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="review_reactions")
