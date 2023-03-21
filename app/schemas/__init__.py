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
    Order,
    OrderNote,
    OrderProductVariation,
    OrderStatus,
    Product,
    ProductImage,
    ProductPrice,
    ProductPropertyValue,
    ProductReview,
    ProductReviewPhoto,
    ProductVariationCount,
    ProductVariationValue,
    ResetToken,
    Seller,
    SellerFavorite,
    Supplier,
    Tags,
    User,
    UserAddress,
    UserImage,
    UserNotification,
    UserPaymentCredentials,
    UserSearch,
)
from .requests import ChangePassword, PaginationQuery, Register
from .schema import ApplicationResponse

__all__ = (
    "Admin",
    "Category",
    "CategoryProperty",
    "CategoryPropertyType",
    "CategoryPropertyValue",
    "CategoryVariation",
    "CategoryVariationType",
    "CategoryVariationValue",
    "Company",
    "CompanyImage",
    "Order",
    "OrderNote",
    "OrderProductVariation",
    "OrderStatus",
    "Product",
    "ProductImage",
    "ProductPrice",
    "ProductPropertyValue",
    "ProductReview",
    "ProductReviewPhoto",
    "ProductVariationCount",
    "ProductVariationValue",
    "ResetToken",
    "Seller",
    "SellerFavorite",
    "Supplier",
    "Tags",
    "User",
    "UserAddress",
    "UserImage",
    "UserNotification",
    "UserPaymentCredentials",
    "UserSearch",
    "ChangePassword",
    "PaginationQuery",
    "Register",
    "ApplicationResponse",
    "JWT",
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
