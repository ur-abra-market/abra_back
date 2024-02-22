from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from orm.core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product_review import ProductReviewModel


class ProductReviewPhotoModel(mixins.ProductReviewIDMixin, ORMModel):
    image_url: Mapped[types.text]
    serial_number: Mapped[types.small_int]

    review: Mapped[Optional[ProductReviewModel]] = relationship(back_populates="photos")
