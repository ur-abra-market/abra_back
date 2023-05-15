from __future__ import annotations

from sqlalchemy.orm import Mapped

from .core import ORMModel, category_property_value_fk, sku_id_fk


class SkuPropertyModel(ORMModel):
    """
    Все проперти (не меняющиеся характеристики), присущие sku.
    """

    sku_id: Mapped[sku_id_fk]
    category_property_value_id: Mapped[category_property_value_fk]
