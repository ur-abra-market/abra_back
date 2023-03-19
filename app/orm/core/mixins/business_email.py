from __future__ import annotations

from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from app.orm.core.types import str_200


class BusinessEmailMixin:
    @declared_attr.directive
    def business_email(self) -> Mapped[str_200]:
        return mapped_column(
            unique=True,
            index=True,
        )
