from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, decimal_2_1, mixins, str_200
from .core.types import bool_true, str_36, text

if TYPE_CHECKING:
    from .category import CategoryModel
    from .category_property_value import CategoryPropertyValueModel
    from .category_variation_value import CategoryVariationValueModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .tags import TagsModel


class ProductModel(mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[str_200]
    description: Mapped[Optional[text]]
    datetime: Mapped[datetime]
    grade_average: Mapped[decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[int] = mapped_column(default=0)
    uuid: Mapped[UUID] = mapped_column(default=uuid4)
    is_active: Mapped[bool_true]

    category: Mapped[Optional[CategoryModel]] = relationship(back_populates="products")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="products")
    tags: Mapped[List[TagsModel]] = relationship(back_populates="product")
    properties: Mapped[List[CategoryPropertyValueModel]] = relationship(
        secondary="product_property_value",
        back_populates="products",
    )
    variations: Mapped[List[CategoryVariationValueModel]] = relationship(
        secondary="product_variation_value",
        back_populates="products",
    )
    favorites_by_users: Mapped[List[SellerModel]] = relationship(
        secondary="seller_favorite", back_populates="favorites"
    )
