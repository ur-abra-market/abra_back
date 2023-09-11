from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .brand import BrandModel
    from .bundle import BundleModel
    from .category import CategoryModel
    from .product_image import ProductImageModel
    from .product_review import ProductReviewModel
    from .property_value import PropertyValueModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .tags import TagModel
    from .variation_value import VariationValueModel


class ProductModel(mixins.BrandIDMixin, mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[types.str_200]
    description: Mapped[Optional[types.text]]
    datetime: Mapped[types.moscow_datetime_timezone]
    grade_average: Mapped[types.decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[types.big_int] = mapped_column(default=0)
    is_active: Mapped[types.bool_true]

    bundles: Mapped[List[BundleModel]] = relationship(back_populates="product")
    category: Mapped[Optional[CategoryModel]] = relationship(back_populates="products")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="products")
    images: Mapped[List[ProductImageModel]] = relationship(back_populates="product")
    tags: Mapped[List[TagModel]] = relationship(back_populates="product", secondary="product_tags")
    properties: Mapped[List[PropertyValueModel]] = relationship(
        secondary="property_value_to_product",
        back_populates="products",
    )
    variations: Mapped[List[VariationValueModel]] = relationship(
        secondary="variation_value_to_product",
        back_populates="products",
    )
    favorites_by_users: Mapped[List[SellerModel]] = relationship(
        secondary="seller_favorite", back_populates="favorites"
    )
    reviews: Mapped[List[ProductReviewModel]] = relationship(back_populates="product")
    brand: Mapped[List[BrandModel]] = relationship(back_populates="products")
