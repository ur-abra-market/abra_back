from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, str_14, str_50, text

if TYPE_CHECKING:
    from .seller_delivery import SellerDeliveryModel


class CountryModel(ORMModel):
    country: Mapped[str_50] = mapped_column(unique=True)
    country_code: Mapped[str_14]
    flag: Mapped[text]

    deliveries: Mapped[List[SellerDeliveryModel]] = relationship(back_populates="country")
