from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from ..types import str_15


class PhoneMixin:
    phone: Mapped[Optional[str_15]] = mapped_column(nullable=True)
