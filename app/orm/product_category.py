from __future__ import annotations

from .core import ORMModel, mixins


class ProductCategoryModel(mixins.ProductIDMixin, mixins.CategoryIDMixin, ORMModel):
    ...
