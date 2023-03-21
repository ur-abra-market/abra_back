from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class ProductReviewPhotoModel(mixins.ProductReviewIDMixin, ORMModel):
    image_url: Mapped[text]
    serial_number: Mapped[int]
