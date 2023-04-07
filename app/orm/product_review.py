from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins
from .core import text as t

if TYPE_CHECKING:
    from .product_review_photo import ProductReviewPhotoModel


class ProductReviewModel(mixins.ProductIDMixin, mixins.SellerIDMixin, ORMModel):
    text: Mapped[t]
    grade_overall: Mapped[int]
    datetime: Mapped[dt.datetime]

    photos: Mapped[List[ProductReviewPhotoModel]] = relationship()
