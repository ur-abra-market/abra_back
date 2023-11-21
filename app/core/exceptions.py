from typing import Any, Optional

from fastapi import HTTPException
from starlette import status


class ApplicationException(HTTPException):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Application Error"
    headers: Optional[dict[str, Any]] = None

    def __init__(
        self,
        status_code: Optional[int] = None,
        detail: Optional[str] = None,
        headers: Optional[dict[str, Any]] = None,
        *args,
    ):
        if detail is not None:
            self.detail = detail
        if status_code is not None:
            self.status_code = status_code
        if headers is not None:
            self.headers = headers
        super().__init__(self.status_code, self.detail, self.headers, *args)


class NotFoundException(ApplicationException):
    status_code: int = status.HTTP_404_NOT_FOUND
    detail: str = "Object Not Found Error"


class ForbiddenException(ApplicationException):
    status_code: int = status.HTTP_403_FORBIDDEN
    detail: str = "Forbidden"


class BadRequestException(ApplicationException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Bad Request"


class AlreadyExistException(ApplicationException):
    status_code: int = status.HTTP_409_CONFLICT
    detail: str = "Already Exist"


class UnprocessableEntityException(ApplicationException):
    status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail: str = "Unprocessable Entity"


class GoogleOAuthException(ApplicationException):
    status_code: int = status.HTTP_400_BAD_REQUEST
    detail: str = "Google AOuth exception"
