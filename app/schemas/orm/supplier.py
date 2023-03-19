from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from app.schemas.orm.schema import ORMSchema

if TYPE_CHECKING:
    from app.schemas.orm.company import Company
    from app.schemas.orm.product import Product
    from app.schemas.orm.user import User


class Supplier(ORMSchema):
    user_id: int
    license_number: Optional[str] = None
    grade_average: float = 0.0
    additional_info: Optional[str] = None
    user: Optional[User] = None
    company: Optional[Company] = None
    products: List[Product]
