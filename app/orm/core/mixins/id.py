from __future__ import annotations

from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class IDMixin:
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
