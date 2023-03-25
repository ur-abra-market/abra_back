from .bodies import (
    BodyChangePassword as BodyChangePasswordRequest,
    BodyLogin as BodyLoginRequest,
    BodyProductReview as BodyProductReviewRequest,
    BodyRegister as BodyRegisterRequest,
)
from .queries import (
    QueryMyEmail as QueryMyEmailRequest,
    QueryPagination as QueryPaginationRequest,
    QueryTokenConfirmation as QueryTokenConfirmationRequest,
)

__all__ = (
    "BodyChangePasswordRequest",
    "BodyLoginRequest",
    "BodyProductReviewRequest",
    "BodyRegisterRequest",
    "QueryMyEmailRequest",
    "QueryPaginationRequest",
    "QueryTokenConfirmationRequest",
)
