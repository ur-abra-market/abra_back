from __future__ import annotations

import datetime as dt
from typing import Optional

from ...schema import ApplicationSchema


class ProductPriceUpload(ApplicationSchema):
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: dt.datetime = dt.datetime.now()
    end_date: dt.datetime = dt.datetime(year=2099, month=1, day=1)
