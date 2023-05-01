from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, str_20, str_30, str_50, str_100

if TYPE_CHECKING:
    from .seller import SellerModel


class SellerAddressModel(mixins.SellerIDMixin, mixins.NameMixin, mixins.PhoneMixin, ORMModel):
    country: Mapped[Optional[str_30]]
    area: Mapped[Optional[str_50]]
    city: Mapped[Optional[str_50]]
    street: Mapped[Optional[str_100]]
    building: Mapped[Optional[str_20]]
    apartment: Mapped[Optional[str_20]]
    postal_code: Mapped[Optional[str_20]]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="addresses")
