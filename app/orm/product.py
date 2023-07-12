from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .category import CategoryModel
    from .category_property_value import CategoryPropertyValueModel
    from .category_variation_value import CategoryVariationValueModel
    from .product_image import ProductImageModel
    from .product_price import ProductPriceModel
    from .product_review import ProductReviewModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .tags import TagsModel


class ProductModel(mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[types.str_200]
    description: Mapped[Optional[types.text]]
    datetime: Mapped[types.moscow_datetime_timezone]
    grade_average: Mapped[types.decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[types.big_int] = mapped_column(default=0)
    uuid: Mapped[UUID] = mapped_column(default=uuid4)
    is_active: Mapped[types.bool_true]

    category: Mapped[Optional[CategoryModel]] = relationship(back_populates="products")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="products")
    images: Mapped[List[ProductImageModel]] = relationship(back_populates="product")
    tags: Mapped[List[TagsModel]] = relationship(back_populates="product")
    prices: Mapped[List[ProductPriceModel]] = relationship(back_populates="product")
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
    reviews: Mapped[List[ProductReviewModel]] = relationship(back_populates="product")
