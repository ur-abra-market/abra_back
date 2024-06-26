from __future__ import annotations

from typing import Optional

from ...mixins import PhoneNumber
from ...schema import ApplicationSchema


class SellerAddressUpdate(PhoneNumber, ApplicationSchema):
    address_id: int
    is_main: bool = False
    country_id: Optional[int] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    area: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    building: Optional[str] = None
    apartment: Optional[str] = None
    postal_code: Optional[str] = None
