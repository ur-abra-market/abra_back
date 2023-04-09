from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .product import Product


class ProductPrice(mixins.ProductIDMixin, ORMSchema):
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: dt.datetime
    end_date: Optional[dt.datetime] = None
    product: Optional[Product] = None
