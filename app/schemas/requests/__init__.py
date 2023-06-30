from .bodies import BodyChangeEmail as BodyChangeEmailRequest
from .bodies import BodyChangePassword as BodyChangePasswordRequest
from .bodies import BodyCompanyData as BodyCompanyDataRequest
from .bodies import BodyCompanyDataUpdate as BodyCompanyDataUpdateRequest
from .bodies import BodyCompanyImageData as BodyCompanyImageDataRequest
from .bodies import BodyCompanyPhoneData as BodyCompanyPhoneDataRequest
from .bodies import BodyCompanyPhoneDataUpdate as BodyCompanyPhoneDataUpdateRequest
from .bodies import BodyLogin as BodyLoginRequest
from .bodies import BodyOrderStatus as BodyOrderStatusRequest
from .bodies import BodyProductCompilation as BodyProductCompilationRequest
from .bodies import BodyProductPagination as BodyProductPaginationRequest
from .bodies import BodyProductPriceUpload as BodyProductPriceUploadRequest
from .bodies import BodyProductReview as BodyProductReviewRequest
from .bodies import BodyProductUpload as BodyProductUploadRequest
from .bodies import BodyRegister as BodyRegisterRequest
from .bodies import BodyResetPassword as BodyResetPasswordRequest
from .bodies import BodySellerAddress as BodySellerAddressRequest
from .bodies import BodySellerAddressPhoneData as BodySellerAddressPhoneDataRequest
from .bodies import BodySellerAddressUpdate as BodySellerAddressUpdateRequest
from .bodies import BodySellerNotificationUpdate as BodySellerNotificationUpdateRequest
from .bodies import BodySupplierData as BodySupplierDataRequest
from .bodies import BodySupplierDataUpdate as BodySupplierDataUpdateRequest
from .bodies import (
    BodySupplierNotificationUpdate as BodySupplierNotificationUpdateRequest,
)
from .bodies import BodyUserData as BodyUserDataRequest
from .bodies import BodyUserDataUpdate as BodyUserDataUpdateRequest
from .queries import QueryMyEmail as QueryMyEmailRequest
from .queries import QueryPagination as QueryPaginationRequest
from .queries import QueryTokenConfirmation as QueryTokenConfirmationRequest

__all__ = (
    "BodyChangeEmailRequest",
    "BodyChangePasswordRequest",
    "BodyCompanyDataRequest",
    "BodyCompanyDataUpdateRequest",
    "BodyCompanyImageDataRequest",
    "BodyCompanyPhoneDataRequest",
    "BodyCompanyPhoneDataUpdateRequest",
    "BodyLoginRequest",
    "BodyOrderStatusRequest",
    "BodyProductCompilationRequest",
    "BodyProductUploadRequest",
    "BodyProductPaginationRequest",
    "BodyProductPriceUploadRequest",
    "BodyProductReviewRequest",
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
    "QueryMyEmailRequest",
    "QueryPaginationRequest",
    "QueryTokenConfirmationRequest",
    "BodySellerAddressPhoneDataRequest",
)
