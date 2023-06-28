from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .country import CountryModel
    from .seller_address import SellerAddressModel


class SellerAddressPhoneModel(mixins.PhoneMixin, mixins.SellerAddressIDMixin, ORMModel):
    seller_address: Mapped[Optional[SellerAddressModel]] = relationship(back_populates="phone")
    country: Mapped[Optional[CountryModel]] = relationship(back_populates="phone")
