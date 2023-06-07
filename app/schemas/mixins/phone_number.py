from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PhoneNumber(BaseModel):
    country_id: Optional[int] = None
    phone_number: Optional[str] = None
