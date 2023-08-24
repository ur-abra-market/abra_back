from __future__ import annotations

from dataclasses import dataclass

from corecrud import CRUD, Mappings

from orm import (
    CategoryModel,
    CategoryToPropertyModel,
    CategoryToVariationTypeModel,
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
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductReviewReactionModel,
    ProductVariationCountModel,
    PropertyTypeModel,
    PropertyValueModel,
    PropertyValueToProductModel,
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
    VariationTypeModel,
    VariationValueModel,
    VariationValueToProductModel,
)


@dataclass(init=False, eq=False, repr=False, frozen=True)
class _CRUD:
    raws: CRUD[None] = CRUD(
        model=None,
        cursor_cls=Mappings,
    )
    categories: CRUD[CategoryModel] = CRUD(CategoryModel)
    categories_properties: CRUD[CategoryToPropertyModel] = CRUD(CategoryToPropertyModel)
    categories_property_types: CRUD[PropertyTypeModel] = CRUD(PropertyTypeModel)
    categories_property_values: CRUD[PropertyValueModel] = CRUD(PropertyValueModel)
    categories_variation_types: CRUD[VariationTypeModel] = CRUD(VariationTypeModel)
    categories_variations: CRUD[CategoryToVariationTypeModel] = CRUD(CategoryToVariationTypeModel)
    categories_variation_values: CRUD[VariationValueModel] = CRUD(VariationValueModel)
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
    products_property_values: CRUD[PropertyValueToProductModel] = CRUD(PropertyValueToProductModel)
    products_variation_values: CRUD[VariationValueToProductModel] = CRUD(
        VariationValueToProductModel
    )
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
