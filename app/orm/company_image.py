from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, text


class CompanyImageModel(mixins.CompanyIDMixin, ORMModel):
    url: Mapped[Optional[text]]
    serial_number: Mapped[text]
