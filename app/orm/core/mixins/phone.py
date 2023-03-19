from __future__ import annotations

from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.orm.core.types import str_15


class PhoneMixin:
    @declared_attr.directive
    def phone(self) -> Mapped[str_15]:
        return mapped_column(nullable=True)
