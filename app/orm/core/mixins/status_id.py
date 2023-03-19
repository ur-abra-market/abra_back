from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core.types import order_status_fk


class StatusIDMixin:
    status_id: Mapped[order_status_fk]
