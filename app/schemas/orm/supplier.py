from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .core import ORMSchema, mixins

if TYPE_CHECKING:
    from .company import Company
    from .product import Product
    from .user import User
    from .user_address import UserAddress


class Supplier(mixins.UserIDMixin, ORMSchema):
    license_number: Optional[str] = None
    grade_average: float = 0.0
    additional_info: Optional[str] = None
    user: Optional[User] = None
    company: Optional[Company] = None
    products: Optional[List[Product]] = None
    addresses: Optional[UserAddress] = None
