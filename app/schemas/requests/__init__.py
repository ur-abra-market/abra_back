from .bodies import BodyChangePassword as BodyChangePasswordRequest
from .bodies import BodyLogin as BodyLoginRequest
from .bodies import BodyPhoneNumber as BodyPhoneNumberRequest
from .bodies import BodyProductReview as BodyProductReviewRequest
from .bodies import BodyRegister as BodyRegisterRequest
from .bodies import BodyUserAddress as BodyUserAddressRequest
from .bodies import BodyUserAddressUpdate as BodyUserAddressUpdateRequest
from .bodies import BodyUserData as BodyUserDataRequest
from .bodies import BodyUserNotification as BodyUserNotificationRequest
from .queries import QueryMyEmail as QueryMyEmailRequest
from .queries import QueryPagination as QueryPaginationRequest
from .queries import QueryProductCompilation as QueryProductCompilationRequest
from .queries import QueryTokenConfirmation as QueryTokenConfirmationRequest

__all__ = (
    "BodyChangePasswordRequest",
    "BodyLoginRequest",
    "BodyPhoneNumberRequest",
    "BodyProductReviewRequest",
    "BodyRegisterRequest",
    "BodyUserAddressRequest",
    "BodyUserAddressUpdateRequest",
    "BodyUserDataRequest",
    "BodyUserNotificationRequest",
    "QueryMyEmailRequest",
    "QueryPaginationRequest",
    "QueryProductCompilationRequest",
    "QueryTokenConfirmationRequest",
)
