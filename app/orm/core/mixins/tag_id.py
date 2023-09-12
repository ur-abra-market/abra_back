from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from ..constraints import order_status_fk
from ..types import order_status_fk_type


class TagIDMixin:
    status_id: Mapped[Optional[order_status_fk_type]] = order_status_fk
