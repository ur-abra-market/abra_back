from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class SellerFavorite(ORMSchema):
    seller_id: int
    product_id: int
