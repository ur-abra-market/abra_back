from __future__ import annotations

from datetime import datetime

from app.schemas.orm.schema import ORMSchema


class Order(ORMSchema):
    seller_id: int
    datetime: datetime
    is_car: bool = True
