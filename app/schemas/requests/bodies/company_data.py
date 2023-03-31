from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema


class CompanyData(ApplicationSchema):
    name: str
    business_sector: str
    is_manufacturer: int
    year_established: Optional[int] = None
    number_of_employees: Optional[int] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    business_email: Optional[EmailStr] = None
    address: Optional[str] = None
