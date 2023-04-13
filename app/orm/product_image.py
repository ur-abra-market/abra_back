from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, small_int, text

if TYPE_CHECKING:
    from .product import ProductModel


class ProductImageModel(mixins.ProductIDMixin, ORMModel):
    image_url: Mapped[text]
    serial_number: Mapped[small_int]

    product: Mapped[ProductModel] = relationship(back_populates="images")
