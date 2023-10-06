from __future__ import annotations

from sqlalchemy.orm import Mapped

from ..constraints import order_id_fk
from ..types import order_id_fk_type


class OrderIDMixin:
    order_id: Mapped[order_id_fk_type] = order_id_fk
