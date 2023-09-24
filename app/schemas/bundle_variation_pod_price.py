from __future__ import annotations

import datetime as dt

from typing import Optional

from .core import ORMSchema


class BundleVariationPodPrice(ORMSchema):
    value: float
    discount: float
    min_quantity: int
    bundle_variation_pod_id: int
    start_date: dt.datetime
    end_date: Optional[dt.datetime] = None
