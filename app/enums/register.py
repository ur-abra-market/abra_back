from enum import Enum


class RegisterResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2
    WRONG_DATA = 3
    EMAIL_ALREADY_EXIST = 4
