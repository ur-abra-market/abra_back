from __future__ import annotations

from .core import ORMSchema


class Country(ORMSchema):
    country: str
    country_code: str
    flag: str
