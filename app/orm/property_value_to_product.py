from __future__ import annotations

from .core import ORMModel, mixins


class PropertyValueToProductModel(mixins.ProductIDMixin, mixins.PropertyValueIDMixin, ORMModel):
    ...
