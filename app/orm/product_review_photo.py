from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .product_review import ProductReviewModel


class ProductReviewPhotoModel(mixins.ProductReviewIDMixin, ORMModel):
    image_url: Mapped[text]
    serial_number: Mapped[int]

    review: Mapped[Optional[ProductReviewModel]] = relationship(back_populates="photos")
