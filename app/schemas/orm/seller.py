from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .schema import ORMSchema

if TYPE_CHECKING:
    from .product import Product
    from .user import User


class Seller(ORMSchema):
    user_id: int
    user: Optional[User] = None
    favorites: Optional[List[Product]] = None
