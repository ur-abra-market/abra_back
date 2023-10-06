from __future__ import annotations

from .core import ORMModel, mixins


class CategoryToPropertyTypeModel(mixins.CategoryIDMixin, mixins.PropertyTypeIDMixin, ORMModel):
    ...
