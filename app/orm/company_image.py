from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, small_int, text


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[text]]
    order: Mapped[small_int]
