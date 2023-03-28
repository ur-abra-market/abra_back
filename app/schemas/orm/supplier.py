from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from .schema import ORMSchema

if TYPE_CHECKING:
    from .company import Company
    from .product import Product
    from .user import User


class Supplier(ORMSchema):
    user_id: int
    license_number: Optional[str] = None
    grade_average: float = 0.0
    additional_info: Optional[str] = None
    user: Optional[User] = None
    company: Optional[Company] = None
    products: Optional[List[Product]] = None
