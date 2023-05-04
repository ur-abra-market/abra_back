from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from enums import CurrencyEnum

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .country import CountryModel
    from .seller import SellerModel


class SellerDeliveryModel(mixins.SellerIDMixin, mixins.CountryIDMixin, ORMModel):
    currency: Mapped[CurrencyEnum]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="deliveries")
    country: Mapped[Optional[CountryModel]] = relationship(back_populates="deliveries")
