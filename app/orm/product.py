from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.orm.core import ORMModel, decimal_2_1, mixins, str_200
from app.orm.core.types import bool_true, str_36

if TYPE_CHECKING:
    from app.orm.category import CategoryModel
    from app.orm.category_property_value import CategoryPropertyValueModel
    from app.orm.category_variation_value import CategoryVariationValueModel
    from app.orm.seller import SellerModel
    from app.orm.supplier import SupplierModel
    from app.orm.tags import TagsModel


class ProductModel(mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[str_200]
    description: Mapped[Optional[str]]
    datetime: Mapped[datetime]
    grade_average: Mapped[decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[int] = mapped_column(default=0)
    uuid: Mapped[str_36]
    is_active: Mapped[bool_true]

    category: Mapped[Optional[CategoryModel]] = relationship(
        CategoryModel, back_populates="products"
    )
    supplier: Mapped[Optional[SupplierModel]] = relationship(
        SupplierModel, back_populates="products"
    )
    tags: Mapped[List[TagsModel]] = relationship(TagsModel, back_populates="product")
    properties: Mapped[List[CategoryPropertyValueModel]] = relationship(
        CategoryPropertyValueModel,
        secondary="product_property_values",
        back_populates="products",
    )
    variations: Mapped[List[CategoryVariationValueModel]] = relationship(
        CategoryVariationValueModel,
        secondary="product_variation_values",
        back_populates="products",
    )
    favorites_by_users: Mapped[List[SellerModel]] = relationship(
        SellerModel, secondary="seller_favorites", back_populates="favorites"
    )
