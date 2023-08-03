from __future__ import annotations

from utils.pydantic import BaseJSONSchema, PhoneStr

from ..schema import ApplicationSchema


class CompanyPhoneDataUpload(BaseJSONSchema, ApplicationSchema):
    country_id: int
    phone_number: PhoneStr
