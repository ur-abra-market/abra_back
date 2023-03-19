from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from app.orm.core import ORMModel, mixins

if TYPE_CHECKING:
    from app.orm.product import ProductModel
    from app.orm.user import UserModel


class SellerModel(mixins.UserIDMixin, ORMModel):
    user: Mapped[Optional[UserModel]] = relationship(UserModel, back_populates="seller")
    favorites: Mapped[List[ProductModel]] = relationship(
        ProductModel,
        secondary="seller_favorites",
        back_populates="favorites_by_users",
    )
