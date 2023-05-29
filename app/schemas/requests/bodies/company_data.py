from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema
from ._phone_number import PhoneNumber


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
