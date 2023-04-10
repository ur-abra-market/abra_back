from .bodies import BodyChangeEmail as BodyChangeEmailRequest
from .bodies import BodyChangePassword as BodyChangePasswordRequest
from .bodies import BodyCompanyData as BodyCompanyDataRequest
from .bodies import BodyLogin as BodyLoginRequest
from .bodies import BodyPhoneNumber as BodyPhoneNumberRequest
from .bodies import BodyProductReview as BodyProductReviewRequest
from .bodies import BodyProductUpload as BodyProductUploadRequest
from .bodies import BodyRegister as BodyRegisterRequest
from .bodies import BodyResetPassword as BodyResetPasswordRequest
from .bodies import BodySupplierData as BodySupplierDataRequest
from .bodies import BodyUserAddress as BodyUserAddressRequest
from .bodies import BodyUserAddressUpdate as BodyUserAddressUpdateRequest
from .bodies import BodyUserData as BodyUserDataRequest
from .bodies import BodyUserNotification as BodyUserNotificationRequest
from .queries import QueryMyEmail as QueryMyEmailRequest
from .queries import QueryPagination as QueryPaginationRequest
from .queries import QueryProductCompilation as QueryProductCompilationRequest
from .queries import QueryTokenConfirmation as QueryTokenConfirmationRequest

__all__ = (
    "BodyChangeEmailRequest",
    "BodyChangePasswordRequest",
    "BodyCompanyDataRequest",
    "BodyLoginRequest",
    "BodyPhoneNumberRequest",
    "BodyProductUploadRequest",
    "BodyProductReviewRequest",
    "BodyRegisterRequest",
    "BodyResetPasswordRequest",
    "BodySupplierDataRequest",
    "BodyUserAddressRequest",
    "BodyUserAddressUpdateRequest",
    "BodyUserDataRequest",
    "BodyUserNotificationRequest",
    "QueryMyEmailRequest",
    "QueryPaginationRequest",
    "QueryProductCompilationRequest",
    "QueryTokenConfirmationRequest",
)
