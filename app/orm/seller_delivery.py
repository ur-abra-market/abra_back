from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, types, str_4

if TYPE_CHECKING: 
    from .country import CountryModel
    from .seller import SellerModel


class SellerDeliveryModel(ORMModel): 
    seller_id: Mapped[types.seller_id_fk]
    currency: Mapped[str_4]
    country_id: Mapped[types.country_id_fk]

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="delivery")
    country: Mapped[Optional[CountryModel]] = relationship(back_populates="delivery")