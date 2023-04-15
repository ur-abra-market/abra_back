from __future__ import annotations

from dataclasses import dataclass

from orm import (
    AdminModel,
    CategoryModel,
    CategoryPropertyModel,
    CategoryPropertyTypeModel,
    CategoryPropertyValueModel,
    CategoryVariationModel,
    CategoryVariationTypeModel,
    CategoryVariationValueModel,
    CompanyImageModel,
    CompanyModel,
    OrderModel,
    OrderNoteModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductPriceModel,
    ProductPropertyValueModel,
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductReviewReactionModel,
    ProductVariationCountModel,
    ProductVariationValueModel,
    ResetTokenModel,
    SellerAddressModel,
    SellerFavoriteModel,
    SellerImageModel,
    SellerModel,
    SupplierModel,
    TagsModel,
    UserCredentialsModel,
    UserModel,
    UserNotificationModel,
    UserSearchModel,
)

from ._orm import ORM as _ORM
from .orders_products_variation import OrdersProductsVariation
from .raws import Raws


@dataclass(
    init=False,
    eq=False,
    repr=False,
    frozen=True,
)
class ORM:
    raws: Raws = Raws()
    admins: _ORM[AdminModel] = _ORM(AdminModel)
    categories: _ORM[CategoryModel] = _ORM(CategoryModel)
    categories_properties: _ORM[CategoryPropertyModel] = _ORM(CategoryPropertyModel)
    categories_property_types: _ORM[CategoryPropertyTypeModel] = _ORM(CategoryPropertyTypeModel)
    categories_property_values: _ORM[CategoryPropertyValueModel] = _ORM(CategoryPropertyValueModel)
    categories_variation_types: _ORM[CategoryVariationTypeModel] = _ORM(CategoryVariationTypeModel)
    categories_variations: _ORM[CategoryVariationModel] = _ORM(CategoryVariationModel)
    categories_variation_values: _ORM[CategoryVariationValueModel] = _ORM(
        CategoryVariationValueModel
    )
    companies: _ORM[CompanyModel] = _ORM(CompanyModel)
    companies_images: _ORM[CompanyImageModel] = _ORM(CompanyImageModel)
    orders: _ORM[OrderModel] = _ORM(OrderModel)
    orders_notes: _ORM[OrderNoteModel] = _ORM(OrderNoteModel)
    orders_products_variation: OrdersProductsVariation = OrdersProductsVariation()
    orders_statuses: _ORM[OrderStatusModel] = _ORM(OrderStatusModel)
    products: _ORM[ProductModel] = _ORM(ProductModel)
    products_images: _ORM[ProductImageModel] = _ORM(ProductImageModel)
    products_prices: _ORM[ProductPriceModel] = _ORM(ProductPriceModel)
    products_property_values: _ORM[ProductPropertyValueModel] = _ORM(ProductPropertyValueModel)
    products_variation_values: _ORM[ProductVariationValueModel] = _ORM(ProductVariationValueModel)
    products_reviews: _ORM[ProductReviewModel] = _ORM(ProductReviewModel)
    products_reviews_photos: _ORM[ProductReviewPhotoModel] = _ORM(ProductReviewPhotoModel)
    products_reviews_reactions: _ORM[ProductReviewReactionModel] = _ORM(ProductReviewReactionModel)
    products_variation_counts: _ORM[ProductVariationCountModel] = _ORM(ProductVariationCountModel)
    reset_tokens: _ORM[ResetTokenModel] = _ORM(ResetTokenModel)
    sellers: _ORM[SellerModel] = _ORM(SellerModel)
    sellers_addresses: _ORM[SellerAddressModel] = _ORM(SellerAddressModel)
    sellers_images: _ORM[SellerImageModel] = _ORM(SellerImageModel)
    sellers_favorites: _ORM[SellerFavoriteModel] = _ORM(SellerFavoriteModel)
    suppliers: _ORM[SupplierModel] = _ORM(SupplierModel)
    tags: _ORM[TagsModel] = _ORM(TagsModel)
    users: _ORM[UserModel] = _ORM(UserModel)
    users_credentials: _ORM[UserCredentialsModel] = _ORM(UserCredentialsModel)
    users_notifications: _ORM[UserNotificationModel] = _ORM(UserNotificationModel)
    users_searches: _ORM[UserSearchModel] = _ORM(UserSearchModel)


orm = ORM()

__all__ = ("orm",)
