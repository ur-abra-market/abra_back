from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, types

if TYPE_CHECKING:
    from .company import CompanyModel
    from .seller_address import SellerAddressModel
    from .seller_address_phone import SellerAddressPhoneModel
    from .user import UserModel


class CountryModel(ORMModel):
    country: Mapped[types.str_50] = mapped_column(unique=True)
    country_code: Mapped[types.str_4]
    country_short: Mapped[types.str_4]
    currency: Mapped[types.text]
    flag: Mapped[types.text]

    addresses: Mapped[List[SellerAddressModel]] = relationship(back_populates="country")
    phone: Mapped[List[SellerAddressPhoneModel]] = relationship(back_populates="country")
    companies: Mapped[List[CompanyModel]] = relationship(back_populates="country")
    users: Mapped[List[UserModel]] = relationship(back_populates="country")
