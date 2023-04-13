from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .supplier import Supplier
    from .user import User


class UserAddress(ORMSchema):
    country: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
    user: Optional[User] = None
    supplier: Optional[Supplier] = None
