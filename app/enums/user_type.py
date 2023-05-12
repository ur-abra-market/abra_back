from enum import Enum

class UserType(str, Enum):
    SELLER: str = "seller"
    SUPPLIER: str = "supplier"
