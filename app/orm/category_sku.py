from __future__ import annotations

from .core import ORMModel, mixins


class CategorySkuModel(mixins.CategoryIDMixin, mixins.SkuIDMixin, ORMModel):
    ...
