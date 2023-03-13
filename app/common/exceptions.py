from typing import Optional

from app.common.enums import ErrorCodes


class InvalidStatusId(Exception):
    pass


class InvalidProductVariationId(Exception):
    pass


class GenericApiException(Exception):
    code: ErrorCodes = ErrorCodes.api_error
    message: str = "Generic Error"
    status_code: int = 500

    def __init__(
        self,
        code: Optional[ErrorCodes] = None,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
        *args,
    ):
        if code is not None:
            self.code = code
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        super().__init__(message, *args)


class AuthException(GenericApiException):
    code: ErrorCodes = ErrorCodes.auth_error
    message: str = "Authentication Error"
    status_code: int = 400


class NotFoundException(GenericApiException):
    code: ErrorCodes = ErrorCodes.not_found_error
    message: str = "Object Not Found Error"
    status_code: int = 404


class BadRequestException(GenericApiException):
    code: ErrorCodes = ErrorCodes.bad_request
    message: str = "Bad Request"
    status_code: int = 400


class SQLError(GenericApiException):
    code: ErrorCodes = ErrorCodes.sql_error
    status_code: int = 400

    def __init__(
        self,
        message: str,
        code: Optional[ErrorCodes] = None,
        status_code: Optional[int] = None,
        *args,
    ):
        super().__init__(code, message, status_code, *args)


class ConfirmError(GenericApiException):
    code: ErrorCodes = ErrorCodes.confirm_error
    status_code: int = 400
    message: str = "Confirm Error"


class ArgError(GenericApiException):
    code: ErrorCodes = ErrorCodes.args_error
    status_code: int = 400
    message: str = "Args Error"


class AlreadyExistError(GenericApiException):
    code: ErrorCodes = ErrorCodes.already_exist
    status_code: int = 400
    message: str = "Already Exist"


class NotExistError(GenericApiException):
    code: ErrorCodes = ErrorCodes.not_exist
    status_code: int = 400
    message: str = "Does not Exist"


class PermissionError(GenericApiException):
    code: ErrorCodes = ErrorCodes.permission_error
    status_code: int = 400
    message: str = "Only Allowed For Admins"
