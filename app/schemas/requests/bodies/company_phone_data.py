from __future__ import annotations

from typing import Optional

from ...mixins import CountryId
from ...schema import ApplicationSchema, BaseJsonSchema


class CompanyPhoneData(BaseJsonSchema, CountryId, ApplicationSchema):
    phone_number: Optional[str] = None
