from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, category_property_value_fk, mixins


class ProductPropertyValueModel(mixins.ProductIDMixin, ORMModel):
    property_value_id: Mapped[category_property_value_fk]
