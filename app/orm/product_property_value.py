from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class ProductPropertyValueModel(mixins.ProductIDMixin, ORMModel):
    property_value_id: Mapped[types.category_property_value_fk]
