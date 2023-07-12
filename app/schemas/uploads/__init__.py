from .change_email import ChangeEmailUpload
from .change_password import ChangePasswordUpload
from .company_data import CompanyDataUpload
from .company_data_update import CompanyDataUpdateUpload
from .company_image_data import CompanyImageDataUpload
from .company_phone_data_update import CompanyPhoneDataUpdateUpload
from .login import LoginUpload
from .my_email import MyEmailUpload
from .order_status import OrderStatusUpload
from .pagination import PaginationUpload
from .product import ProductUpload
from .product_compilation import ProductCompilationUpload
from .product_pagination import ProductPaginationUpload
from .product_price import ProductPriceUpload
from .product_review import ProductReviewUpload
from .register import RegisterUpload
from .reset_password import ResetPasswordUpload
from .seller_address import SellerAddressUpload
from .seller_address_phone_data import SellerAddressPhoneDataUpload
from .seller_address_update import SellerAddressUpdateUpload
from .seller_notifications_update import SellerNotificationsUpdateUpload
from .supplier_data import SupplierDataUpload
from .supplier_data_update import SupplierDataUpdateUpload
from .supplier_notifications_update import SupplierNotificationsUpdateUpload
from .token_confirmation import TokenConfirmationUpload
from .user_data import UserDataUpload
from .user_data_update import UserDataUpdateUpload

__all__ = (
    "ChangeEmailUpload",
    "ChangePasswordUpload",
    "CompanyDataUpdateUpload",
    "CompanyDataUpload",
    "CompanyImageDataUpload",
    "CompanyPhoneDataUpdateUpload",
    "LoginUpload",
    "MyEmailUpload",
    "OrderStatusUpload",
    "PaginationUpload",
    "ProductCompilationUpload",
    "ProductPaginationUpload",
    "ProductPriceUpload",
    "ProductReviewUpload",
    "ProductUpload",
    "RegisterUpload",
    "ResetPasswordUpload",
    "SellerAddressPhoneDataUpload",
    "SellerAddressUpdateUpload",
    "SellerAddressUpload",
    "SellerNotificationsUpdateUpload",
    "SupplierDataUpdateUpload",
    "SupplierDataUpload",
    "SupplierNotificationsUpdateUpload",
    "TokenConfirmationUpload",
    "UserDataUpdateUpload",
    "UserDataUpload",
)

from utils.pydantic import update_forward_refs_helper

update_forward_refs_helper(__all__, globals())