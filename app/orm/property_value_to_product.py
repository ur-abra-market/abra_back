from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class PropertyValueToProductModel(mixins.ProductIDMixin, ORMModel):
    property_value_id: Mapped[types.property_value_fk]
