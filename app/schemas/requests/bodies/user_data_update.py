from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class UserDataUpdate(ApplicationSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_country_code: Optional[str] = None
    phone_number: Optional[str] = None
