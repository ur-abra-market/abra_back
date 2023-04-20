from __future__ import annotations

from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import Mapped

from .core import ORMModel, category_variation_type_fk, mixins


class CategoryVariationModel(mixins.CategoryIDMixin, ORMModel):
    variation_type_id: Mapped[category_variation_type_fk]
    __table_args__ = (UniqueConstraint("category_id", "variation_type_id", name="_cat_var_uc"),)
