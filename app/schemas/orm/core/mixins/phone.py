from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PhoneMixin(BaseModel):
    phone_country_code: Optional[str] = None
    phone_number: Optional[str] = None
