from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TIMESTAMP

from utils import current_datetime_tz_util

from .core import ORMModel, decimal_3_2, decimal_10_2, mixins
from .product import ProductModel

# FIXME: alembic wants
# from ..utils import current_datetime_tz_util



class ProductPriceModel(mixins.ProductIDMixin, ORMModel):
    value: Mapped[decimal_10_2]
    discount: Mapped[Optional[decimal_3_2]]
    min_quantity: Mapped[int]
    product: Mapped[ProductModel] = relationship(back_populates="prices")
    start_date: Mapped[datetime] = mapped_column(
        default=current_datetime_tz_util, type_=TIMESTAMP(timezone=True)
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(type_=TIMESTAMP(timezone=True))
