from typing import Optional
from datetime import datetime

from pydantic import Field

from ...schema import ApplicationSchema
from utils import current_datetime_tz_util


class ProductPrice(ApplicationSchema):
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: Optional[datetime] = Field(default_factory=current_datetime_tz_util)
    end_date: Optional[datetime] = None
