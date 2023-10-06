from __future__ import annotations

from .core import ORMModel, mixins


class CategoryToVariationTypeModel(mixins.CategoryIDMixin, mixins.VariationTypeIDMixin, ORMModel):
    ...
