from __future__ import annotations

from dataclasses import dataclass

from corecrud import CRUD, Mappings

from orm import (
    BrandModel,
    BundlableVariationValueModel,
    BundleModel,
    BundlePodPriceModel,
    BundleVariationModel,
    BundleVariationPodAmountModel,
    BundleVariationPodModel,
    CategoryModel,
    CategoryToPropertyTypeModel,
    CategoryToVariationTypeModel,
    CompanyBusinessSectorToCategoryModel,
    CompanyImageModel,
    CompanyModel,
    CompanyPhoneModel,
    CountryModel,
    EmployeesNumberModel,
    OrderModel,
    OrderStatusModel,
    ProductImageModel,
    ProductModel,
    ProductReviewModel,
    ProductReviewPhotoModel,
    ProductReviewReactionModel,
    ProductTagModel,
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
    TagModel,
    UserCredentialsModel,
    UserModel,
    UserSearchModel,
    VariationTypeModel,
    VariationValueImageModel,
    VariationValueModel,
    VariationValueToProductModel,
)


@dataclass(init=False, eq=False, repr=False, frozen=True)
class _CRUD:
    raws: CRUD[None] = CRUD(
        model=None,
        cursor_cls=Mappings,
    )
    brands: CRUD[BrandModel] = CRUD(BrandModel)
    bundlable_variations_values: CRUD[BundlableVariationValueModel] = CRUD(
        BundlableVariationValueModel
    )
    bundles_pods_prices: CRUD[BundlePodPriceModel] = CRUD(BundlePodPriceModel)
    bundles_variations_pods_amount: CRUD[BundleVariationPodAmountModel] = CRUD(
        BundleVariationPodAmountModel
    )
    bundles_variations_pods: CRUD[BundleVariationPodModel] = CRUD(BundleVariationPodModel)
    bundles_variations: CRUD[BundleVariationModel] = CRUD(BundleVariationModel)
    bundles: CRUD[BundleModel] = CRUD(BundleModel)
    categories: CRUD[CategoryModel] = CRUD(CategoryModel)
    categories_properties: CRUD[CategoryToPropertyTypeModel] = CRUD(CategoryToPropertyTypeModel)
    categories_property_types: CRUD[PropertyTypeModel] = CRUD(PropertyTypeModel)
    categories_property_values: CRUD[PropertyValueModel] = CRUD(PropertyValueModel)
    categories_variation_types: CRUD[VariationTypeModel] = CRUD(VariationTypeModel)
    categories_variations: CRUD[CategoryToVariationTypeModel] = CRUD(CategoryToVariationTypeModel)
    categories_variation_values: CRUD[VariationValueModel] = CRUD(VariationValueModel)
    companies_business_sectors_to_categories: CRUD[CompanyBusinessSectorToCategoryModel] = CRUD(
        CompanyBusinessSectorToCategoryModel
    )
    companies_images: CRUD[CompanyImageModel] = CRUD(CompanyImageModel)
    companies_phones: CRUD[CompanyPhoneModel] = CRUD(CompanyPhoneModel)
    companies: CRUD[CompanyModel] = CRUD(CompanyModel)
    country: CRUD[CountryModel] = CRUD(CountryModel)
    number_employees: CRUD[EmployeesNumberModel] = CRUD(EmployeesNumberModel)
    orders: CRUD[OrderModel] = CRUD(OrderModel)
    orders_statuses: CRUD[OrderStatusModel] = CRUD(OrderStatusModel)
    products: CRUD[ProductModel] = CRUD(ProductModel)
    products_images: CRUD[ProductImageModel] = CRUD(ProductImageModel)
    property_values_to_products: CRUD[PropertyValueToProductModel] = CRUD(
        PropertyValueToProductModel
    )
    variation_values_to_products: CRUD[VariationValueToProductModel] = CRUD(
        VariationValueToProductModel
    )
    products_reviews: CRUD[ProductReviewModel] = CRUD(ProductReviewModel)
    products_reviews_photos: CRUD[ProductReviewPhotoModel] = CRUD(ProductReviewPhotoModel)
    products_reviews_reactions: CRUD[ProductReviewReactionModel] = CRUD(ProductReviewReactionModel)
    products_tags: CRUD[ProductTagModel] = CRUD(ProductTagModel)
    reset_tokens: CRUD[ResetTokenModel] = CRUD(ResetTokenModel)
    sellers: CRUD[SellerModel] = CRUD(SellerModel)
    seller_address_phone: CRUD[SellerAddressPhoneModel] = CRUD(SellerAddressPhoneModel)
    sellers_addresses: CRUD[SellerAddressModel] = CRUD(SellerAddressModel)
    sellers_images: CRUD[SellerImageModel] = CRUD(SellerImageModel)
    sellers_favorites: CRUD[SellerFavoriteModel] = CRUD(SellerFavoriteModel)
    sellers_notifications: CRUD[SellerNotificationsModel] = CRUD(SellerNotificationsModel)
    suppliers: CRUD[SupplierModel] = CRUD(SupplierModel)
    suppliers_notifications: CRUD[SupplierNotificationsModel] = CRUD(SupplierNotificationsModel)
    tags: CRUD[TagModel] = CRUD(TagModel)
    users: CRUD[UserModel] = CRUD(UserModel)
    users_credentials: CRUD[UserCredentialsModel] = CRUD(UserCredentialsModel)
    users_searches: CRUD[UserSearchModel] = CRUD(UserSearchModel)
    variation_values_images: CRUD[VariationValueImageModel] = CRUD(VariationValueImageModel)


crud = _CRUD()

__all__ = ("crud",)
