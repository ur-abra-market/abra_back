from enum import Enum


class RegisterResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2


class LoginResponse(Enum):
    OK = 1
    USER_NOT_FOUND = 2
    INCORRECT_PASSWORD = 3
