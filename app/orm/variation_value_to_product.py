from __future__ import annotations

from .core import ORMModel, mixins


class VariationValueToProductModel(mixins.ProductIDMixin, mixins.VariationValueIDMixin, ORMModel):
    ...
