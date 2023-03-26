from .bodies import (
    BodyChangePassword as BodyChangePasswordRequest,
    BodyLogin as BodyLoginRequest,
    BodyPhoneNumber as BodyPhoneNumberRequest,
    BodyProductReview as BodyProductReviewRequest,
    BodyRegister as BodyRegisterRequest,
    BodyUserAddress as BodyUserAddressRequest,
    BodyUserAddressUpdate as BodyUserAddressUpdateRequest,
    BodyUserData as BodyUserDataRequest,
    BodyUserNotification as BodyUserNotificationRequest,
)
from .queries import (
    QueryMyEmail as QueryMyEmailRequest,
    QueryPagination as QueryPaginationRequest,
    QueryTokenConfirmation as QueryTokenConfirmationRequest,
)

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
    "QueryTokenConfirmationRequest",
)
