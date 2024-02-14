from __future__ import annotations

from orm.core import ORMModel, mixins


class ProductTagModel(mixins.ProductIDMixin, mixins.TagIDMixin, ORMModel):
    ...
