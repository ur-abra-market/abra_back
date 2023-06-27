from __future__ import annotations

from dataclasses import dataclass

from corecrud import CRUD, Mappings

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
    CompanyPhoneModel,
    CountryModel,
    NumberEmployeesModel,
    OrderModel,
    OrderProductVariationModel,
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
    SellerAddressPhoneModel,
    SellerFavoriteModel,
    SellerImageModel,
    SellerModel,
    SellerNotificationsModel,
    SupplierModel,
    SupplierNotificationsModel,
    TagsModel,
    UserCredentialsModel,
    UserModel,
    UserSearchModel,
)


@dataclass(init=False, eq=False, repr=False, frozen=True)
class _CRUD:
    raws: CRUD[None] = CRUD(
        model=None,
        cursor_cls=Mappings,
    )
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
    companies_images: CRUD[CompanyImageModel] = CRUD(CompanyImageModel)
    companies_phones: CRUD[CompanyPhoneModel] = CRUD(CompanyPhoneModel)
    country: CRUD[CountryModel] = CRUD(CountryModel)
    number_employees: CRUD[NumberEmployeesModel] = CRUD(NumberEmployeesModel)
    orders: CRUD[OrderModel] = CRUD(OrderModel)
    orders_products_variation: CRUD[OrderProductVariationModel] = CRUD(OrderProductVariationModel)
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
    sellers_notifications: CRUD[SellerNotificationsModel] = CRUD(SellerNotificationsModel)
    suppliers: CRUD[SupplierModel] = CRUD(SupplierModel)
    suppliers_notifications: CRUD[SupplierNotificationsModel] = CRUD(SupplierNotificationsModel)
    tags: CRUD[TagsModel] = CRUD(TagsModel)
    users: CRUD[UserModel] = CRUD(UserModel)
    users_credentials: CRUD[UserCredentialsModel] = CRUD(UserCredentialsModel)
    users_searches: CRUD[UserSearchModel] = CRUD(UserSearchModel)
    seller_address_phone: CRUD[SellerAddressPhoneModel] = CRUD(SellerAddressPhoneModel)


crud = _CRUD()

__all__ = ("crud",)
