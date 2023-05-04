from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .order import Order
    from .product import Product
    from .product_review_reaction import ProductReviewReaction
    from .seller_address import SellerAddress
    from .seller_delivery import SellerDelivery
    from .seller_image import SellerImage
    from .user import User


class Seller(ORMSchema):
    user: Optional[User] = None
    addresses: Optional[List[SellerAddress]] = None
    image: Optional[SellerImage] = None
    review_reactions: Optional[List[ProductReviewReaction]] = None
    favorites: Optional[List[Product]] = None
    orders: Optional[List[Order]] = None
    delivery: Optional[List[SellerDelivery]] = None


