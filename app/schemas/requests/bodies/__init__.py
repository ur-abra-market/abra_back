from .change_email import ChangeEmail as BodyChangeEmail
from .change_password import ChangePassword as BodyChangePassword
from .company_data import CompanyData as BodyCompanyData
from .login import Login as BodyLogin
from .order_status_id import OrderStatus as BodyOrderStatus
from .phone_number import PhoneNumber as BodyPhoneNumber
from .product import ProductUpload as BodyProductUpload
from .product_compilation import ProductCompilation as BodyProductCompilation
from .product_pagination import ProductPagination as BodyProductPagination
from .product_price import ProductPriceUpload as BodyProductPriceUpload
from .product_review import ProductReview as BodyProductReview
from .register import Register as BodyRegister
from .reset_password import ResetPassword as BodyResetPassword
from .seller_address import SellerAddress as BodySellerAddress
from .seller_address_update import SellerAddressUpdate as BodySellerAddressUpdate
from .seller_delivery_data import SellerDeliveryData as BodySellerDeliveryData
from .supplier_data import SupplierData as BodySupplierData
from .user_data import UserData as BodyUserData
from .user_notification import UserNotification as BodyUserNotification

__all__ = (
    "BodyChangeEmail",
    "BodyChangePassword",
    "BodyCompanyData",
    "BodyLogin",
    "BodyOrderStatus",
    "BodyPhoneNumber",
    "BodyProductCompilation",
    "BodyProductUpload",
    "BodyProductPagination",
    "BodyProductReview",
    "BodyProductPriceUpload",
    "BodyRegister",
    "BodyResetPassword",
    "BodySellerAddress",
    "BodySellerAddressUpdate",
    "BodySellerDeliveryData",
    "BodySupplierData",
    "BodyUserData",
    "BodyUserNotification",
)
