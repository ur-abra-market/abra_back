from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, relationship

from .core import ORMModel, mixins, text

if TYPE_CHECKING:
    from .brand import BrandModel
    from .category import CategoryModel
    from .category_property_value import CategoryPropertyValueModel
    from .supplier import SupplierModel


class SkuModel(mixins.BrandIDMixin, mixins.SupplierIDMixin, ORMModel):
    """
    Артикул. Содержит инфу о товаре, которая не варьируется.
    Категория, бренд, материал и тд.
    """

    name: Mapped[text]

    category: Mapped[CategoryModel] = relationship(back_populates="skus", secondary="category_sku")

    properties: Mapped[Optional[List[CategoryPropertyValueModel]]] = relationship(
        back_populates="skus", secondary="sku_property"
    )
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="skus")
    brand: Mapped[Optional[BrandModel]] = relationship(back_populates="skus")
