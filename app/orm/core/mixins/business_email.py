from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from ..types import str_200


class BusinessEmailMixin:
    business_email: Mapped[str_200] = mapped_column(
        unique=True,
        index=True,
    )
