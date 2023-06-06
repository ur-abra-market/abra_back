from __future__ import annotations

from ...schema import ApplicationSchema


class PhoneNumber(ApplicationSchema):
    phone_country_code: str
    phone_number: str
    country_short: str
