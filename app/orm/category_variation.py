from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, category_variation_type_fk, mixins


class CategoryVariationModel(mixins.CategoryIDMixin, ORMModel):
    variation_type_id: Mapped[category_variation_type_fk]
