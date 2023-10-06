from __future__ import annotations

from .core import ORMModel, mixins


class CompanyBusinessSectorToCategoryModel(
    mixins.CompanyIDMixin, mixins.CategoryIDMixin, ORMModel
):
    ...
