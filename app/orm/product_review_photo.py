from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class ProductReviewPhotoModel(mixins.ProductReviewIDMixin, ORMModel):
    image_url: Mapped[str]
    serial_number: Mapped[int]
