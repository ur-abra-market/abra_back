from __future__ import annotations

from datetime import datetime as dt
from typing import TYPE_CHECKING, Any, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, query_expression, relationship

from orm.core import ORMModel, mixins, types
from orm.property_type import PropertyTypeModel

if TYPE_CHECKING:
    from orm.brand import BrandModel
    from orm.bundle import BundleModel
    from orm.bundle_variation_pod import BundleVariationPodModel
    from orm.category import CategoryModel
    from orm.property_value import PropertyValueModel
    from orm.property_value_to_product import PropertyValueToProductModel
    from orm.seller import SellerModel
    from orm.supplier import SupplierModel
    from orm.tags import TagModel
    from orm.variation_value_to_product import VariationValueToProductModel

    from .product_image import ProductImageModel
    from .product_prices import ProductPriceModel
    from .product_review import ProductReviewModel
    from .product_variation_prices import ProductVariationPriceModel

min_prices: Any = None
max_prices: Any = None


class ProductModel(mixins.BrandIDMixin, mixins.CategoryIDMixin, mixins.SupplierIDMixin, ORMModel):
    name: Mapped[types.str_200]
    description: Mapped[Optional[types.text]]
    grade_average: Mapped[types.decimal_2_1] = mapped_column(default=0.0)
    total_orders: Mapped[types.big_int] = mapped_column(default=0)
    is_active: Mapped[types.bool_true]

    reviews_count = query_expression()
    is_favorite = query_expression()

    prices: Mapped[Optional[List[ProductPriceModel]]] = relationship(
        back_populates="product", lazy="selectin"
    )

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
        viewonly=True,
    )
    property_types: Mapped[List[PropertyTypeModel]] = relationship(
        "PropertyTypeModel",
        secondary="join(PropertyValueToProductModel, PropertyValueModel).join(PropertyTypeModel)",
        viewonly=True,
    )
    property_value_product: Mapped[List[PropertyValueToProductModel]] = relationship(
        back_populates="product"
    )
    property_types: Mapped[List[PropertyTypeModel]] = relationship(
        "PropertyTypeModel",
        secondary="join(PropertyValueToProductModel, PropertyValueModel).join(PropertyTypeModel)",
    )
    property_value_product: Mapped[List[PropertyValueToProductModel]] = relationship(
        back_populates="product"
    )
    product_variations: Mapped[Optional[List[VariationValueToProductModel]]] = relationship(
        back_populates="product",
        lazy="selectin",
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

    @hybrid_property
    def breadcrumbs(self) -> List[CategoryModel]:
        try:
            return [
                self.category,
                self.category.parent,
                self.category.parent.parent,
            ]
        except Exception:
            return []

    @hybrid_property
    def min_price(self):
        variation_prices = [
            price.value for variation in self.product_variations for price in variation.prices
        ]
        return min(variation_prices) if variation_prices else None

    @min_price.expression
    def min_price(cls):
        return (
            select([func.min(ProductVariationPriceModel.value)])
            .where(ProductVariationPriceModel.product_id == cls.id)
            .scalar_subquery()
        )

    @hybrid_property
    def max_price(self):
        variation_prices = [
            price.value for variation in self.product_variations for price in variation.prices
        ]
        return max(variation_prices) if variation_prices else None

    @max_price.expression
    def max_price(cls):
        return (
            select([func.max(ProductVariationPriceModel.value)])
            .where(ProductVariationPriceModel.product_id == cls.id)
            .scalar_subquery()
        )
