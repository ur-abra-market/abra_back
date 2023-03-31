from .change_password import ChangePassword as BodyChangePassword
from .login import Login as BodyLogin
from .phone_number import PhoneNumber as BodyPhoneNumber
from .product import ProductUpload as BodyProductUpload
from .product_review import ProductReview as BodyProductReview
from .register import Register as BodyRegister
from .user_address import UserAddress as BodyUserAddress
from .user_address_update import UserAddressUpdate as BodyUserAddressUpdate
from .user_data import UserData as BodyUserData
from .user_notification import UserNotification as BodyUserNotification

__all__ = (
    "BodyChangePassword",
    "BodyLogin",
    "BodyPhoneNumber",
    "BodyProductReview",
    "BodyRegister",
    "BodyUserAddress",
    "BodyUserAddressUpdate",
    "BodyUserData",
    "BodyUserNotification",
    "BodyProductUpload",
)
