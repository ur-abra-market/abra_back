from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column


class IDMixin:
    id: Mapped[int] = mapped_column(default=0, primary_key=True, index=True)
