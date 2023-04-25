from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, country_code_id_fk, str_50

if TYPE_CHECKING:
    from .country_code import CountryCodeModel


class CountryModel(ORMModel):
    country: Mapped[str_50]

    country_code_id: Mapped[country_code_id_fk]

    country_code: Mapped[Optional[CountryCodeModel]] = relationship(back_populates="country")
