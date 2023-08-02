from __future__ import annotations

from utils.pydantic import PhoneStr

from ..schema import ApplicationSchema


class CompanyPhoneDataRequiredUpdateUpload(ApplicationSchema):
    country_id: int
    phone_number: PhoneStr
