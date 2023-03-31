from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, small_int, text


class ProductImageModel(mixins.ProductIDMixin, ORMModel):
    image_url: Mapped[text]
    serial_number: Mapped[small_int]
