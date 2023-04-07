from __future__ import annotations

from typing import Optional

from .schema import ORMSchema


class Order(ORMSchema):
    seller_id: int
    datetime: datetime
    updated_at: Optional[datetime] = None
    is_car: bool = True
