from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .country import CountryModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .user_credentials import UserCredentialsModel


class UserModel(
    mixins.EmailMixin, mixins.NameMixin, mixins.PhoneMixin, ORMModel
):
    is_verified: Mapped[types.bool_false]
    is_deleted: Mapped[types.bool_false]
    is_supplier: Mapped[types.bool_false]

    credentials: Mapped[Optional[UserCredentialsModel]] = relationship(back_populates="user")

    seller: Mapped[Optional[SellerModel]] = relationship(back_populates="user")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="user")
    country: Mapped[Optional[CountryModel]] = relationship(back_populates="users")
