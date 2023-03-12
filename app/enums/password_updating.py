from enum import Enum


class PasswordUpdatingResponse(Enum):
    OK = 1
    INCORRECT_USER_TYPE = 2
    USER_NOT_FOUND = 3
    INCORRECT_PASSWORD = 4
