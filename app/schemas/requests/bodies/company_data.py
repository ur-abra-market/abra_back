from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...mixins import PhoneNumber
from ...schema import ApplicationSchema


class CompanyData(PhoneNumber, ApplicationSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    number_employees: int
    description: str
    address: str
    logo_url: str
    business_sector: str
    business_email: Optional[EmailStr] = None
    country_id: int
