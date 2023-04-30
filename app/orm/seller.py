from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins

if TYPE_CHECKING:
    from .order import OrderModel
    from .product import ProductModel
    from .product_review_reaction import ProductReviewReactionModel
    from .seller_address import SellerAddressModel
    from .seller_image import SellerImageModel
    from .user import UserModel


class SellerModel(mixins.UserIDMixin, ORMModel):
    user: Mapped[Optional[UserModel]] = relationship(back_populates="seller")
    addresses: Mapped[List[SellerAddressModel]] = relationship(back_populates="seller")
    image: Mapped[Optional[SellerImageModel]] = relationship(back_populates="seller")
    orders: Mapped[List[OrderModel]] = relationship(back_populates="seller")
    review_reactions: Mapped[List[ProductReviewReactionModel]] = relationship(
        back_populates="seller"
    )
    favorites: Mapped[List[ProductModel]] = relationship(
        secondary="seller_favorite",
        back_populates="favorites_by_users",
    )
