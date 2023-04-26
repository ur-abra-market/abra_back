from typing import Optional

from .jwt import JWT
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
    Country,
    CountryCode,
    Order,
    OrderNote,
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
    Supplier,
    Tags,
    User,
    UserNotification,
    UserSearch,
)
from .requests import (
    BodyChangeEmailRequest,
    BodyChangePasswordRequest,
    BodyCompanyDataRequest,
    BodyLoginRequest,
    BodyOrderStatusRequest,
    BodyPhoneNumberRequest,
    BodyProductReviewRequest,
    BodyProductUploadRequest,
    BodyRegisterRequest,
    BodyResetPasswordRequest,
    BodySellerAddressRequest,
    BodySellerAddressUpdateRequest,
    BodySupplierDataRequest,
    BodyUserDataRequest,
    BodyUserNotificationRequest,
    QueryMyEmailRequest,
    QueryPaginationRequest,
    QueryProductCompilationRequest,
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
    "BodyLoginRequest",
    "BodyOrderStatusRequest",
    "BodyPhoneNumberRequest",
    "BodyProductReviewRequest",
    "BodyProductUploadRequest",
    "BodyRegisterRequest",
    "BodyResetPasswordRequest",
    "BodySellerAddressRequest",
    "BodySellerAddressUpdateRequest",
    "BodySupplierDataRequest",
    "BodyUserDataRequest",
    "BodyUserNotificationRequest",
    "Category",
    "CategoryPropertyType",
    "CategoryPropertyValue",
    "CategoryVariationType",
    "CategoryVariationValue",
    "CategoryProperty",
    "CategoryVariation",
    "Company",
    "CompanyImage",
    "Country",
    "CountryCode",
    "ORMSchema",
    "JWT",
    "Order",
    "OrderNote",
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
    "QueryProductCompilationRequest",
    "QueryTokenConfirmationRequest",
    "ResetToken",
    "Seller",
    "SellerAddress",
    "SellerImage",
    "Supplier",
    "Tags",
    "User",
    "UserNotification",
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
