from __future__ import annotations

from app.schemas.orm.schema import ORMSchema


class CategoryVariation(ORMSchema):
    category_id: int
    variation_type_id: int
