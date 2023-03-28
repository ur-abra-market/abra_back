from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .product import ProductModel
    from .user import UserModel


class SellerModel(mixins.UserIDMixin, ORMModel):
    user: Mapped[Optional[UserModel]] = relationship(back_populates="seller")
    favorites: Mapped[List[ProductModel]] = relationship(
        secondary="seller_favorite",
        back_populates="favorites_by_users",
    )
