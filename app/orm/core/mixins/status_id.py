from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from ..types import order_status_fk


class StatusIDMixin:
    status_id: Mapped[Optional[order_status_fk]]
