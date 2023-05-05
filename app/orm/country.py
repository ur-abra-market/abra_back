from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, str_4, str_50, text

if TYPE_CHECKING:
    from enums import CurrencyEnum

    from .seller_address import SellerAddressModel


class CountryModel(ORMModel):
    country: Mapped[str_50] = mapped_column(unique=True)
    country_code: Mapped[str_4]
    currency: Mapped[CurrencyEnum]
    flag: Mapped[text]

    addresses: Mapped[List[SellerAddressModel]] = relationship(back_populates="country")
