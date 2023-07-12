from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class UserDataUpdateUpload(ApplicationSchema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
