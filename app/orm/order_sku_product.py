from __future__ import annotations

from .core import ORMModel, mixins


class OrderSkuProductModel(mixins.SkuProductIDMixin, mixins.OrderWithSkuIDMixin, ORMModel):
    """m2m ордера и артикулы+продукты"""
