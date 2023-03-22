from __future__ import annotations

from typing import Optional

from .schema import ORMSchema


class UserAddress(ORMSchema):
    user_id: int
    country: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None