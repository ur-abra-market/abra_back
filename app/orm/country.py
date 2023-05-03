from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column

from .core import ORMModel, str_14, str_50, text


class CountryModel(ORMModel):
    country: Mapped[str_50] = mapped_column(unique=True)
    country_code: Mapped[str_14]
    flag: Mapped[text]
