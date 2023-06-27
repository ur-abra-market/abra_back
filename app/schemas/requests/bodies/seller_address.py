from __future__ import annotations

from typing import Optional

from ...mixins import CountryId
from ...schema import ApplicationSchema


class SellerAddress(CountryId, ApplicationSchema):
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
