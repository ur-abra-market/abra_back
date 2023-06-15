from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from schemas.orm import Country


class PhoneMixin(BaseModel):
    phone_number: Optional[str] = None
    phone_number_country: Optional[Country] = None
