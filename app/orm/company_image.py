from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, mixins


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[str]]
    serial_number: Mapped[int]
