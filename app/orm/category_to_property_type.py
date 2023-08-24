from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class CategoryToPropertyModel(mixins.CategoryIDMixin, ORMModel):
    property_type_id: Mapped[types.property_type_fk]
