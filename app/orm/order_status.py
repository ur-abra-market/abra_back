from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, str_20


class OrderStatusModel(ORMModel):
    name: Mapped[str_20]
