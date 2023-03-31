from __future__ import annotations

from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, small_int, text


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[text]]
    order: Mapped[small_int]

    __table_args__ = (UniqueConstraint("company_id", "order", name="unique_img_order"),)
