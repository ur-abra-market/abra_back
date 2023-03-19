from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.product import Product


class Tags(ORMSchema):
    product_id: int
    name: str
    product: Optional[Product] = None
