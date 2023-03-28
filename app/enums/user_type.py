from enum import Enum


class UserType(str, Enum):
    SELLER = "seller"
    SUPPLIER = "supplier"
