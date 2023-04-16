from __future__ import annotations

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from ..types import datetime_timezone


class TimestampMixin:
    datetime: Mapped[datetime_timezone] = mapped_column(default=func.now())
    updated_at: Mapped[Optional[datetime_timezone]] = mapped_column(
        onupdate=func.now(), nullable=True
    )
