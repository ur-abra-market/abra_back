from __future__ import annotations

import datetime as dt
from typing import TYPE_CHECKING, Optional

from pydantic import Field

from .core import ORMSchema

if TYPE_CHECKING:
    from .product import Product


class ProductPrice(ORMSchema):
    id: int = Field(return_in_api=False)
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: dt.datetime
    end_date: Optional[dt.datetime] = None
    product: Optional[Product] = Field(return_in_api=False)
