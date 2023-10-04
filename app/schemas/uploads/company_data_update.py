from __future__ import annotations

import datetime
from typing import Optional

from pydantic import Field, validator

from utils.pydantic import EmailStr

from ..schema import ApplicationSchema


class CompanyDataUpdateUpload(ApplicationSchema):
    country_id: Optional[int] = Field(None)
    name: Optional[str] = Field(None)
    is_manufacturer: Optional[bool] = Field(False)
    year_established: Optional[int] = Field(None)
    employees_number_id: Optional[int] = Field(None)
    description: Optional[str] = Field(None, min_length=0)
    address: Optional[str] = Field(None, min_length=0)
    business_email: Optional[EmailStr] = Field(None)

    @validator("year_established")
    def value_must_equal_bar(cls, v):
        current_year = datetime.date.today().year
        if v not in range(1960, current_year):
            raise ValueError(f"value must be between 1960 and {current_year}")

        return v
