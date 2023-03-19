from __future__ import annotations

from sqlalchemy.orm import Mapped, declared_attr, mapped_column


class IDMixin:
    @declared_attr.directive
    def id(self) -> Mapped[int]:
        return mapped_column(
            primary_key=True,
            index=True,
        )
