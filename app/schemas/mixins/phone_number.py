from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .country_id import CountryId


class PhoneNumber(CountryId, BaseModel):
    phone_number: Optional[str] = None
