from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Mapped

from .core import ORMModel, mixins, types


class PropertyValueToProductModel(mixins.ProductIDMixin, mixins.PropertyValueIDMixin, ORMModel):
    optional_value: Mapped[Optional[types.text]]
