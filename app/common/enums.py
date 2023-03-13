import enum
from enum import Enum


# will we us it?
class UserTypes(Enum):
    SELLERS = 1
    SUPPLIERS = 2
    ADMINS = 3


class RegisterResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2
    WRONG_DATA = 3
    EMAIL_ALREADY_EXIST = 4


class LoginResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2
    USER_NOT_FOUND = 3
    INCORRECT_PASSWORD = 4


class PasswordUpdatingResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2
    USER_NOT_FOUND = 3
    INCORRECT_PASSWORD = 4


class StrEnum(str, enum.Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name


class ErrorCodes(StrEnum):
    api_error = enum.auto()
    auth_error = enum.auto()
    not_found_error = enum.auto()
    permission_error = enum.auto()
    server_error = enum.auto()
    sql_error = enum.auto()
    confirm_error = enum.auto()
    args_error = enum.auto()
    already_exist = enum.auto()
    not_exist = enum.auto()
    bad_request = enum.auto()
