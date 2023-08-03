from __future__ import annotations

from typing import Optional

from pydantic import Field

from utils.pydantic import PhoneStr

from ..schema import ApplicationSchema


class CompanyPhoneDataUpdateUpload(ApplicationSchema):
    country_id: int = None
    phone_number: Optional[PhoneStr] = Field(None, min_length=0)
