from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .product import ProductModel

from .core import ORMModel, decimal_3_2, decimal_10_2, mixins, moscow_datetime_timezone


class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    value: Mapped[decimal_10_2]
    discount: Mapped[Optional[decimal_3_2]]
    min_quantity: Mapped[int]

    start_date: Mapped[moscow_datetime_timezone]
    end_date: Mapped[Optional[moscow_datetime_timezone]]

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="prices")
