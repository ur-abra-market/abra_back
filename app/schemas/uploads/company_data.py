from __future__ import annotations

from typing import Optional

from pydantic import Field

from utils.pydantic import BaseJSONSchema, EmailStr

from ..schema import ApplicationSchema


class CompanyDataUpload(BaseJSONSchema, ApplicationSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    employees_number: int
    description: Optional[str] = Field(None, min_length=0)
    address: Optional[str]
    business_sector: str
    business_email: Optional[EmailStr] = None
    country_id: int
