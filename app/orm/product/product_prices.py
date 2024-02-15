from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from orm.core import ORMModel, mixins, types

if TYPE_CHECKING:
    from orm.product import ProductModel


class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    value: Mapped[types.decimal_10_3]
    discount: Mapped[types.decimal_3_2]
    start_date: Mapped[types.datetime]
    end_date: Mapped[types.datetime]
    min_quantity: Mapped[types.int]
    product: Mapped[Optional[ProductModel]] = relationship(back_populates="prices")
