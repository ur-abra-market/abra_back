from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class UserData(ApplicationSchema):
    first_name: str
    last_name: Optional[str] = None
    phone_country_code: str
    phone_number: str
