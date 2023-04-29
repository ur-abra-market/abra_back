from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, decimal_3_2, decimal_10_2, mixins, moscow_datetime_timezone

if TYPE_CHECKING:
    from .product import ProductModel


class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    value: Mapped[decimal_10_2]
    discount: Mapped[Optional[decimal_3_2]]
    min_quantity: Mapped[int]

    start_date: Mapped[moscow_datetime_timezone]
    end_date: Mapped[moscow_datetime_timezone] = mapped_column(
        default=dt.datetime(year=2099, month=1, day=1)
    )

    product: Mapped[Optional[ProductModel]] = relationship(back_populates="prices")
