from .change_email import ChangeEmail as BodyChangeEmail
from .change_password import ChangePassword as BodyChangePassword
from .company_data import CompanyData as BodyCompanyData
from .login import Login as BodyLogin
from .phone_number import PhoneNumber as BodyPhoneNumber
from .product import ProductUpload as BodyProductUpload
from .product_review import ProductReview as BodyProductReview
from .register import Register as BodyRegister
from .reset_password import ResetPassword as BodyResetPassword
from .supplier_data import SupplierData as BodySupplierData
from .user_address import UserAddress as BodyUserAddress
from .user_address_update import UserAddressUpdate as BodyUserAddressUpdate
from .user_data import UserData as BodyUserData
from .user_notification import UserNotification as BodyUserNotification

__all__ = (
    "BodyChangeEmail",
    "BodyChangePassword",
    "BodyCompanyData",
    "BodyLogin",
    "BodyPhoneNumber",
    "BodyProductUpload",
    "BodyProductReview",
    "BodyRegister",
    "BodyResetPassword",
    "BodySupplierData",
    "BodyUserAddress",
    "BodyUserAddressUpdate",
    "BodyUserData",
    "BodyUserNotification",
)
