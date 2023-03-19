from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.orm.core.types import datetime_timezone


class TimestampMixin:
    @declared_attr.directive
    def created_at(self) -> Mapped[datetime_timezone]:
        return mapped_column(
            server_default=func.now(),
        )

    @declared_attr.directive
    def updated_at(self) -> Mapped[datetime_timezone]:
        return mapped_column(server_onupdate=func.now())
