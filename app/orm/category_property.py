from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class CategoryPropertyModel(mixins.CategoryIDMixin, ORMModel):
    property_type_id: Mapped[types.category_property_type_fk]
