from __future__ import annotations

from typing import Optional

from pydantic import Field

from utils.pydantic import EmailStr

from ..schema import ApplicationSchema


class CompanyDataUpdateUpload(ApplicationSchema):
    country_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    is_manufacturer: Optional[bool] = Field(False)
    year_established: Optional[int] = Field(None)
    employees_number: Optional[int] = Field(None)
    description: Optional[str] = Field(None, min_length=0)
    address: Optional[str] = Field(None, min_length=0)
    business_sector: Optional[str] = Field(None)
    business_email: Optional[EmailStr] = Field(None)
