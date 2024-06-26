from typing import Optional

from .orm import (
    Admin,
    Category,
    CategoryProperty,
    CategoryPropertyType,
    CategoryPropertyValue,
    CategoryVariation,
    CategoryVariationType,
    CategoryVariationValue,
    Company,
    CompanyImage,
    CompanyPhone,
    Country,
    NumberEmployees,
    Order,
    OrderProductVariation,
    OrderStatus,
    ORMSchema,
    Product,
    ProductImage,
    ProductPrice,
    ProductReview,
    ProductReviewPhoto,
    ProductReviewReaction,
    ProductVariationCount,
    ProductVariationValue,
    ResetToken,
    Seller,
    SellerAddress,
    SellerImage,
    SellerNotifications,
    Supplier,
    SupplierNotifications,
    Tags,
    User,
    UserSearch,
)
from .requests import (
    BodyChangeEmailRequest,
    BodyChangePasswordRequest,
    BodyCompanyDataRequest,
    BodyCompanyDataUpdateRequest,
    BodyCompanyImageDataRequest,
    BodyCompanyPhoneDataUpdateRequest,
    BodyLoginRequest,
    BodyOrderStatusRequest,
    BodyProductCompilationRequest,
    BodyProductPaginationRequest,
    BodyProductReviewRequest,
    BodyProductUploadRequest,
    BodyRegisterRequest,
    BodyResetPasswordRequest,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    BodySellerNotificationUpdateRequest,
    BodySupplierDataRequest,
    BodySupplierDataUpdateRequest,
    BodySupplierNotificationUpdateRequest,
    BodyUserDataRequest,
    BodyUserDataUpdateRequest,
    QueryMyEmailRequest,
    QueryPaginationRequest,
    QueryTokenConfirmationRequest,
)
from .schema import ApplicationORMSchema, ApplicationResponse, ApplicationSchema

__all__ = (
    "Admin",
    "ApplicationResponse",
    "ApplicationSchema",
    "ApplicationORMSchema",
    "BodyChangeEmailRequest",
    "BodyChangePasswordRequest",
    "BodyCompanyDataRequest",
    "BodyCompanyDataUpdateRequest",
    "BodyCompanyImageDataRequest",
    "BodyCompanyPhoneDataUpdateRequest",
    "BodyLoginRequest",
    "BodyOrderStatusRequest",
    "BodyProductReviewRequest",
    "BodyProductCompilationRequest",
    "BodyProductUploadRequest",
    "BodyProductPaginationRequest",
    "BodyRegisterRequest",
    "BodyResetPasswordRequest",
    "BodySellerAddressRequest",
    "BodySellerAddressUpdateRequest",
    "BodySellerNotificationUpdateRequest",
    "BodySupplierDataRequest",
    "BodySupplierDataUpdateRequest",
    "BodySupplierNotificationUpdateRequest",
    "BodyUserDataRequest",
    "BodyUserDataUpdateRequest",
    "Category",
    "CategoryPropertyType",
    "CategoryPropertyValue",
    "CategoryVariationType",
    "CategoryVariationValue",
    "CategoryProperty",
    "CategoryVariation",
    "Company",
    "CompanyImage",
    "CompanyPhone",
    "NumberEmployees",
    "Country",
    "ORMSchema",
    "Order",
    "OrderProductVariation",
    "OrderStatus",
    "Product",
    "ProductImage",
    "ProductPrice",
    "ProductReview",
    "ProductVariationValue",
    "ProductReviewPhoto",
    "ProductReviewReaction",
    "ProductVariationCount",
    "QueryMyEmailRequest",
    "QueryPaginationRequest",
    "QueryTokenConfirmationRequest",
    "ResetToken",
    "Seller",
    "SellerAddress",
    "SellerImage",
    "SellerNotifications",
    "Supplier",
    "SupplierNotifications",
    "Tags",
    "User",
    "UserSearch",
)


for _entity_name in __all__:
    _entity = globals()[_entity_name]
    if not hasattr(_entity, "update_forward_refs"):
        continue
    _entity.update_forward_refs(
        **{k: v for k, v in globals().items() if k in __all__},
        **{"Optional": Optional},
    )

del _entity
del _entity_name
