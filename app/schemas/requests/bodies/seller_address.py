from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema
from ._phone_number import PhoneNumber


class SellerAddress(PhoneNumber, ApplicationSchema):
    country_id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
