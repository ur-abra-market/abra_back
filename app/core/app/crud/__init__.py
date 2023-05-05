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
    CountryModel,
    NumberEmployeesModel,
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

from .crud import CRUD
from .orders_products_variation import OrdersProductsVariation
from .raws import Raws


@dataclass(init=False, eq=False, repr=False, frozen=True)
class _CRUD:
    raws: Raws = Raws()
    admins: CRUD[AdminModel] = CRUD(AdminModel)
    categories: CRUD[CategoryModel] = CRUD(CategoryModel)
    categories_properties: CRUD[CategoryPropertyModel] = CRUD(CategoryPropertyModel)
    categories_property_types: CRUD[CategoryPropertyTypeModel] = CRUD(CategoryPropertyTypeModel)
    categories_property_values: CRUD[CategoryPropertyValueModel] = CRUD(CategoryPropertyValueModel)
    categories_variation_types: CRUD[CategoryVariationTypeModel] = CRUD(CategoryVariationTypeModel)
    categories_variations: CRUD[CategoryVariationModel] = CRUD(CategoryVariationModel)
    categories_variation_values: CRUD[CategoryVariationValueModel] = CRUD(
        CategoryVariationValueModel
    )
    companies: CRUD[CompanyModel] = CRUD(CompanyModel)
    number_employees: CRUD[NumberEmployeesModel] = CRUD(NumberEmployeesModel)
    companies_images: CRUD[CompanyImageModel] = CRUD(CompanyImageModel)
    country: CRUD[CountryModel] = CRUD(CountryModel)
    orders: CRUD[OrderModel] = CRUD(OrderModel)
    orders_notes: CRUD[OrderNoteModel] = CRUD(OrderNoteModel)
    orders_products_variation: OrdersProductsVariation = OrdersProductsVariation()
    orders_statuses: CRUD[OrderStatusModel] = CRUD(OrderStatusModel)
    products: CRUD[ProductModel] = CRUD(ProductModel)
    products_images: CRUD[ProductImageModel] = CRUD(ProductImageModel)
    products_prices: CRUD[ProductPriceModel] = CRUD(ProductPriceModel)
    products_property_values: CRUD[ProductPropertyValueModel] = CRUD(ProductPropertyValueModel)
    products_variation_values: CRUD[ProductVariationValueModel] = CRUD(ProductVariationValueModel)
    products_reviews: CRUD[ProductReviewModel] = CRUD(ProductReviewModel)
    products_reviews_photos: CRUD[ProductReviewPhotoModel] = CRUD(ProductReviewPhotoModel)
    products_reviews_reactions: CRUD[ProductReviewReactionModel] = CRUD(ProductReviewReactionModel)
    products_variation_counts: CRUD[ProductVariationCountModel] = CRUD(ProductVariationCountModel)
    reset_tokens: CRUD[ResetTokenModel] = CRUD(ResetTokenModel)
    sellers: CRUD[SellerModel] = CRUD(SellerModel)
    sellers_addresses: CRUD[SellerAddressModel] = CRUD(SellerAddressModel)
    sellers_images: CRUD[SellerImageModel] = CRUD(SellerImageModel)
    sellers_favorites: CRUD[SellerFavoriteModel] = CRUD(SellerFavoriteModel)
    suppliers: CRUD[SupplierModel] = CRUD(SupplierModel)
    tags: CRUD[TagsModel] = CRUD(TagsModel)
    users: CRUD[UserModel] = CRUD(UserModel)
    users_credentials: CRUD[UserCredentialsModel] = CRUD(UserCredentialsModel)
    users_notifications: CRUD[UserNotificationModel] = CRUD(UserNotificationModel)
    users_searches: CRUD[UserSearchModel] = CRUD(UserSearchModel)


crud = _CRUD()

__all__ = (
    "crud",
    "CRUD",
)
