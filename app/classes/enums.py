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
