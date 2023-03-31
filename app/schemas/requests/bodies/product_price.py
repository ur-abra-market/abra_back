from datetime import datetime
from typing import Optional

from pydantic import Field

from utils import current_datetime_tz_util

from ...schema import ApplicationSchema


class ProductPrice(ApplicationSchema):
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: Optional[datetime] = Field(default_factory=current_datetime_tz_util)
    end_date: Optional[datetime] = None
