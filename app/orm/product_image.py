from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel


class ProductImageModel(mixins.ProductIDMixin, ORMModel):
    image_url: Mapped[types.text]
    order: Mapped[types.small_int]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="images")
