from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from ..types import str_200


class EmailMixin:
    email: Mapped[str_200] = mapped_column(
        unique=True,
        index=True,
    )
