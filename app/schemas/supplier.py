from __future__ import annotations

from pydantic import root_validator
from typing import TYPE_CHECKING, List, Optional, Dict

from .core import ORMSchema

if TYPE_CHECKING:
    from .company import Company
    from .product import Product
    from .supplier_notifications import SupplierNotifications
    from .user import User


class Supplier(ORMSchema):
    license_number: Optional[str] = None
    grade_average: float = 0.0
    additional_info: Optional[str] = None

    user: Optional[User] = None
    notifications: Optional[SupplierNotifications] = None
    company: Optional[Company] = None
    products: Optional[List[Product]] = None

    @root_validator
    def user_info(cls, values: Dict) -> Dict:
        values["user"] = {
            "first_name": values["user"].first_name,
            "last_name": values["user"].last_name,
            "is_verified": values["user"].is_verified,
        }
        return values
