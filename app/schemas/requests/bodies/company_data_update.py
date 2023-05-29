from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema
from ._phone_number import PhoneNumber


class CompanyDataUpdate(PhoneNumber, ApplicationSchema):
    name: Optional[str] = None
    country_id: Optional[int] = None
    is_manufacturer: Optional[bool] = False
    year_established: Optional[int] = None
    number_employees: Optional[int] = None
    description: Optional[str] = None
    address: Optional[str] = None
    logo_url: Optional[str] = None
    business_sector: Optional[str] = None
    business_email: Optional[EmailStr] = None
