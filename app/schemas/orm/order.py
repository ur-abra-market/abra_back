from __future__ import annotations

import datetime as dt
from typing import Optional

from .schema import ORMSchema


class Order(ORMSchema):
    seller_id: int
    datetime: dt.datetime
    updated_at: Optional[dt.datetime] = None
    is_car: bool = True
