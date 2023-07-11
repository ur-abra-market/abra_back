from __future__ import annotations

from typing import Optional

from ...mixins import CountryId
from ...schema import ApplicationSchema


class CompanyPhoneData(CountryId, ApplicationSchema):
    phone_number: Optional[str] = None
