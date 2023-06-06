from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, bool_false, mixins, str_20, str_50, str_100

if TYPE_CHECKING:
    from .country import CountryModel
    from .seller import SellerModel


class SellerAddressModel(mixins.SellerIDMixin, mixins.NameMixin, mixins.PhoneMixin, ORMModel):
    is_main: Mapped[bool_false]

    area: Mapped[Optional[str_50]]
    city: Mapped[Optional[str_50]]
    street: Mapped[Optional[str_100]]
    building: Mapped[Optional[str_20]]
    apartment: Mapped[Optional[str_20]]
    postal_code: Mapped[Optional[str_20]]

    country: Mapped[Optional[CountryModel]] = relationship(back_populates="addresses")
    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="addresses")
