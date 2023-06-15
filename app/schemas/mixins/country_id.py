from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class CountryId(BaseModel):
    country_id: Optional[int] = None
