from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, small_int, text

if TYPE_CHECKING:
    from .product import ProductModel


class ProductImageModel(mixins.ProductIDMixin, ORMModel):
    image_url: Mapped[text]
    order: Mapped[small_int]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="images")
