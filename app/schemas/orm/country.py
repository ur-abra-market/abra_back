from __future__ import annotations

from typing import Optional

from .core import ORMSchema


class Country(ORMSchema):
    country: str
    country_code: str
    flag: Optional[str]
