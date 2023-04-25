from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, str_4

if TYPE_CHECKING:
    from .country import CountryModel


class CountryCodeModel(ORMModel):
    code: Mapped[str_4]

    country: Mapped[Optional[CountryModel]] = relationship(back_populates="country_code")
