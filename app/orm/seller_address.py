from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .country import CountryModel
    from .seller import SellerModel
    from .seller_address_phone import SellerAddressPhoneModel


class SellerAddressModel(mixins.SellerIDMixin, mixins.NameMixin, mixins.CountryIDMixin, ORMModel):
    is_main: Mapped[types.bool_false]

    area: Mapped[Optional[types.str_50]]
    city: Mapped[Optional[types.str_50]]
    street: Mapped[Optional[types.str_100]]
    building: Mapped[Optional[types.str_20]]
    apartment: Mapped[Optional[types.str_20]]
    postal_code: Mapped[Optional[types.str_20]]

    country: Mapped[Optional[CountryModel]] = relationship(back_populates="addresses")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="addresses")
    phone: Mapped[Optional[SellerAddressPhoneModel]] = relationship(
        back_populates="seller_address"
    )
