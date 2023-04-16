from enum import Enum


class UserType(str, Enum):
    SELLER = "sellers"
    SUPPLIER = "suppliers"
