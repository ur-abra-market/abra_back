from __future__ import annotations

from orm import (
    AdminModel,
    CategoryModel,
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
    ProductVariationCountModel,
    ProductVariationValueModel,
    ResetTokenModel,
    SellerModel,
    SupplierModel,
    TagsModel,
    UserAddressModel,
    UserCredentialsModel,
    UserImageModel,
    UserModel,
    UserNotificationModel,
    UserPaymentCredentialsModel,
    UserSearchModel,
)

from .accessor import ORMAccessor
from .orders_products_variation import OrdersProductsVariation


class ORM:
    def __init__(self) -> None:
        self.admins: ORMAccessor[AdminModel] = ORMAccessor(AdminModel)
        self.categories: ORMAccessor[CategoryModel] = ORMAccessor(CategoryModel)
        self.categories_property_types: ORMAccessor[CategoryPropertyTypeModel] = ORMAccessor(
            CategoryPropertyTypeModel
        )
        self.categories_property_values: ORMAccessor[CategoryPropertyValueModel] = ORMAccessor(
            CategoryPropertyValueModel
        )
        self.categories_variation_types: ORMAccessor[CategoryVariationTypeModel] = ORMAccessor(
            CategoryVariationTypeModel
        )
        self.categories_variations: ORMAccessor[CategoryVariationModel] = ORMAccessor(
            CategoryVariationModel
        )
        self.categories_variation_values: ORMAccessor[CategoryVariationValueModel] = ORMAccessor(
            CategoryVariationValueModel
        )
        self.companies: ORMAccessor[CompanyModel] = ORMAccessor(CompanyModel)
        self.companies_images: ORMAccessor[CompanyImageModel] = ORMAccessor(CompanyImageModel)
        self.orders: ORMAccessor[OrderModel] = ORMAccessor(OrderModel)
        self.orders_notes: ORMAccessor[OrderNoteModel] = ORMAccessor(OrderNoteModel)
        self.orders_products_variation: OrdersProductsVariation = OrdersProductsVariation()
        self.orders_statuses: ORMAccessor[OrderStatusModel] = ORMAccessor(OrderStatusModel)
        self.products: ORMAccessor[ProductModel] = ORMAccessor(ProductModel)
        self.products_images: ORMAccessor[ProductImageModel] = ORMAccessor(ProductImageModel)
        self.products_prices: ORMAccessor[ProductPriceModel] = ORMAccessor(ProductPriceModel)
        self.products_property_values: ORMAccessor[ProductPropertyValueModel] = ORMAccessor(
            ProductPropertyValueModel
        )
        self.products_variation_values: ORMAccessor[ProductVariationValueModel] = ORMAccessor(
            ProductVariationValueModel
        )

        self.products_reviews: ORMAccessor[ProductReviewModel] = ORMAccessor(ProductReviewModel)
        self.products_reviews_photos: ORMAccessor[ProductReviewPhotoModel] = ORMAccessor(
            ProductReviewPhotoModel
        )
        self.products_variation_counts: ORMAccessor[ProductVariationCountModel] = ORMAccessor(
            ProductVariationCountModel
        )
        self.reset_tokens: ORMAccessor[ResetTokenModel] = ORMAccessor(ResetTokenModel)
        self.sellers: ORMAccessor[SellerModel] = ORMAccessor(SellerModel)
        self.suppliers: ORMAccessor[SupplierModel] = ORMAccessor(SupplierModel)
        self.tags: ORMAccessor[TagsModel] = ORMAccessor(TagsModel)
        self.users: ORMAccessor[UserModel] = ORMAccessor(UserModel)
        self.users_addresses: ORMAccessor[UserAddressModel] = ORMAccessor(UserAddressModel)
        self.users_credentials: ORMAccessor[UserCredentialsModel] = ORMAccessor(
            UserCredentialsModel
        )
        self.users_images: ORMAccessor[UserImageModel] = ORMAccessor(UserImageModel)
        self.users_notifications: ORMAccessor[UserNotificationModel] = ORMAccessor(
            UserNotificationModel
        )
        self.users_payments_credentials: ORMAccessor[UserPaymentCredentialsModel] = ORMAccessor(
            UserPaymentCredentialsModel
        )
        self.users_searches: ORMAccessor[UserSearchModel] = ORMAccessor(UserSearchModel)
