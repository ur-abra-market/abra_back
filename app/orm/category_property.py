from __future__ import annotations

from sqlalchemy.orm import Mapped

from app.orm.core import ORMModel, category_property_type_fk, mixins


class CategoryPropertyModel(mixins.CategoryIDMixin, ORMModel):
    property_type_id: Mapped[category_property_type_fk]
