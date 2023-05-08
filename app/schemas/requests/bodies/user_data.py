from __future__ import annotations

from ...schema import ApplicationSchema


class UserData(ApplicationSchema):
    first_name: str
    last_name: str
    phone_country_code: str
    phone_number: str
