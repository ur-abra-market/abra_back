from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, str_20, str_30, str_50, str_100

if TYPE_CHECKING:
    from .user import UserModel


class UserAddressModel(mixins.UserIDMixin, ORMModel):
    country: Mapped[Optional[str_30]]
    area: Mapped[Optional[str_50]]
    city: Mapped[Optional[str_50]]
    street: Mapped[Optional[str_100]]
    building: Mapped[Optional[str_20]]
    apartment: Mapped[Optional[str_20]]
    postal_code: Mapped[Optional[str_20]]

    user: Mapped[Optional[UserModel]] = relationship(back_populates="addresses")
