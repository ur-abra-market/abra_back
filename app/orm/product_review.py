from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins
from .core import text as t

if TYPE_CHECKING:
    from .product import ProductModel
    from .product_review_photo import ProductReviewPhotoModel


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[t]
    grade_overall: Mapped[int]
    datetime: Mapped[dt.datetime]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="reviews")
    photos: Mapped[List[ProductReviewPhotoModel]] = relationship(back_populates="review")
