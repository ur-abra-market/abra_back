from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema
from ._phone_number import PhoneNumber


class CompanyData(PhoneNumber, ApplicationSchema):
    name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int] = None
    number_of_employees: Optional[int] = None
    description: Optional[str] = None
    business_email: Optional[EmailStr] = None
    address: Optional[str] = None
