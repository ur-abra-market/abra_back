from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..types import order_id_fk


class OrderIDMixin:
    order_id: Mapped[order_id_fk]
