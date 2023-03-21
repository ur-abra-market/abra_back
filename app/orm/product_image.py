from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class ProductImageModel(mixins.ProductIDMixin, ORMModel):
    image_url: Mapped[text]
    serial_number: Mapped[int]
