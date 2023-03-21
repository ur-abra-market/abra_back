from __future__ import annotations

from datetime import datetime
from typing import Optional

import pytz
from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, decimal_3_2, decimal_10_2, mixins

TIMEZONE = pytz.timezone("Europe/Moscow")


class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    value: Mapped[decimal_10_2]
    discount: Mapped[Optional[decimal_3_2]]
    min_quantity: Mapped[int]

    start_date: Mapped[datetime] = mapped_column(default=datetime.now(tz=TIMEZONE))
    end_date: Mapped[Optional[datetime]]
