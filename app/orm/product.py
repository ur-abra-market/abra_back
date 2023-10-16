from __future__ import annotations

from datetime import datetime as dt
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .core import ORMModel, mixins, types

if TYPE_CHECKING:
    from .brand import BrandModel
    from .bundle import BundleModel
    from .bundle_variation_pod import BundleVariationPodModel
    from .category import CategoryModel
    from .product_image import ProductImageModel
    from .product_prices import ProductPriceModel
    from .product_review import ProductReviewModel
    from .property_value import PropertyValueModel
    from .seller import SellerModel
    from .supplier import SupplierModel
    from .tags import TagModel
    from .variation_value_to_product import VariationValueToProductModel


class ProductModel(mixins.BrandIDMixin, mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[types.str_200]
    description: Mapped[Optional[types.text]]
    grade_average: Mapped[types.decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[types.big_int] = mapped_column(default=0)
    is_active: Mapped[types.bool_true]

    prices: Mapped[Optional[List[ProductPriceModel]]] = relationship(back_populates="product")
    bundles: Mapped[Optional[List[BundleModel]]] = relationship(back_populates="product")
    bundle_variation_pods: Mapped[Optional[List[BundleVariationPodModel]]] = relationship(
        back_populates="product"
    )
    category: Mapped[Optional[CategoryModel]] = relationship(back_populates="products")
    supplier: Mapped[Optional[SupplierModel]] = relationship(back_populates="products")
    images: Mapped[Optional[List[ProductImageModel]]] = relationship(back_populates="product")
    tags: Mapped[Optional[List[TagModel]]] = relationship(
        back_populates="product", secondary="product_tag"
    )
    properties: Mapped[Optional[List[PropertyValueModel]]] = relationship(
        secondary="property_value_to_product",
        back_populates="products",
    )
    product_variations: Mapped[Optional[List[VariationValueToProductModel]]] = relationship(
        back_populates="product"
    )
    favorites_by_users: Mapped[Optional[List[SellerModel]]] = relationship(
        secondary="seller_favorite", back_populates="favorites"
    )
    reviews: Mapped[Optional[List[ProductReviewModel]]] = relationship(back_populates="product")
    brand: Mapped[Optional[List[BrandModel]]] = relationship(back_populates="products")

    @hybrid_property
    def up_to_discount(self) -> Optional[float]:
        product_discounts = [
            price.discount
            for price in self.prices
            if price.start_date <= dt.now() <= price.end_date
        ] or [0]
        max_product_discount = max(product_discounts)

        max_product_var_discount = 0
        for variation in self.product_variations:
            variation_discounts = [
                price.discount
                for price in variation.prices
                if price.start_date <= dt.now() <= price.end_date
            ] or [0]
            max_variation_discount = max(variation_discounts)
            max_product_var_discount = max(max_variation_discount, max_product_var_discount)

        return max_product_discount + max_product_var_discount
