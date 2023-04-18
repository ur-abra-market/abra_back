from typing import Optional

from pydantic import BaseModel


class PhoneNumber(BaseModel):
    phone_country_code: Optional[str] = None
    phone_number: Optional[str] = None
