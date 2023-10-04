from __future__ import annotations

import datetime
from typing import Optional

from pydantic import Field, validator

from utils.pydantic import BaseJSONSchema, EmailStr

from ..schema import ApplicationSchema


class CompanyDataUpload(BaseJSONSchema, ApplicationSchema):
    name: str
    is_manufacturer: bool = False
    year_established: int
    employees_number_id: int
    description: Optional[str] = Field(None, min_length=0)
    address: Optional[str]
    business_email: Optional[EmailStr] = None
    country_id: int

    @validator("year_established")
    def value_must_equal_bar(cls, v):
        current_year = datetime.date.today().year
        if v not in range(1960, current_year):
            raise ValueError(f"value must be between 1960 and {current_year}")

        return v
