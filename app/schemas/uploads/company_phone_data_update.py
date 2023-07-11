from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class CompanyPhoneDataUpdateUpload(ApplicationSchema):
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
