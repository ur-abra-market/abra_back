from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .product import ProductModel


class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    price: Mapped[types.decimal_10_2]
    discount: Mapped[types.decimal_3_2]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="prices")
