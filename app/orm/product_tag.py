from __future__ import annotations

from .core import ORMModel, mixins


class ProductTagModel(mixins.ProductIDMixin, mixins.TagIDMixin, ORMModel):
    ...
