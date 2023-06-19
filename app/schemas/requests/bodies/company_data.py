from __future__ import annotations

from typing import Optional

from pydantic import EmailStr

from ...schema import ApplicationSchema


class CompanyData(ApplicationSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    number_employees: int
    description: Optional[str]
    address: Optional[str]
    logo_url: Optional[str]
    business_sector: str
    business_email: Optional[EmailStr] = None
    country_id: int
