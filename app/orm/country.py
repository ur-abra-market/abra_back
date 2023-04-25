from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, str_50, types

if TYPE_CHECKING:
    from .country_code import CountryCodeModel


class CountryModel(ORMModel):
    country: Mapped[str_50]
    country_code_id: Mapped[types.country_code_id_fk]

    code: Mapped[Optional["CountryCodeModel"]] = relationship(back_populates="country")
