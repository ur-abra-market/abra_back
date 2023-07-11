from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from ..types import big_int


class IDMixin:
    id: Mapped[big_int] = mapped_column(primary_key=True, index=True)
