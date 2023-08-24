from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class CategoryToVariationTypeModel(mixins.CategoryIDMixin, ORMModel):
    variation_type_id: Mapped[types.variation_type_fk]
