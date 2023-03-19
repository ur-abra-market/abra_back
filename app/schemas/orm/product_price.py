from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.schemas.orm.schema import ORMSchema


class ProductPrice(ORMSchema):
    product_id: int
    value: float
    discount: Optional[float] = None
    min_quantity: int
    start_date: datetime
    end_date: Optional[datetime] = None
