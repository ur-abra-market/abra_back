from __future__ import annotations

from typing import Optional

from .schema import ApplicationSchema


class UserDataUpload(ApplicationSchema):
    first_name: str
    last_name: str
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
