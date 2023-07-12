from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class CategoryVariationModel(mixins.CategoryIDMixin, ORMModel):
    variation_type_id: Mapped[types.category_variation_type_fk]
