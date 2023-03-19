from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.product import Product
    from app.schemas.orm.user import User


class Seller(ORMSchema):
    user_id: int
    user: Optional[User] = None
    favorites: List[Product]
