import datetime as dt
from typing import Optional

from .bundle import Bundle
from .schema import ApplicationSchema


class BundlePrice(ApplicationSchema):
    bundle_id: int
    price: float
    discount: float
    start_date: dt.datetime
    end_date: dt.datetime
    min_quantity: int

    bundle: Optional[Bundle] = None
