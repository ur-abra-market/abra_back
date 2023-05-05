from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema
from ._phone_number import PhoneNumber


class CompanyDataUpdate(PhoneNumber, ApplicationSchema):
    name: Optional[str] = None
    is_manufacturer: Optional[bool] = False
    year_established: Optional[int]
    number_employees: Optional[int]
    description: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    business_sector: str
    business_email: Optional[EmailStr] = None
