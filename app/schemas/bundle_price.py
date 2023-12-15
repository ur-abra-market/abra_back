import datetime as dt
from typing import Optional

from .bundle import Bundle
from .core import ORMSchema


class BundlePrice(ORMSchema):
    bundle_id: int
    price: float
    discount: float
    start_date: dt.datetime
    end_date: dt.datetime
    min_quantity: int

    bundle: Optional[Bundle] = None
