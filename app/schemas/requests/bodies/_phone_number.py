from typing import Optional

from pydantic import BaseModel


class PhoneNumber(BaseModel):
    phone_number: Optional[str] = None
