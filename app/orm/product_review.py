from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .product_review_photo import ProductReviewPhotoModel
    from .product import ProductModel


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[text]
    grade_overall: Mapped[int]
    datetime: Mapped[datetime]

    photos: Mapped[List[ProductReviewPhotoModel]] = relationship()
    product: Mapped[ProductModel] = relationship(back_populates="reviews")
