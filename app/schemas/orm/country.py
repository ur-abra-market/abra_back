from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .country_code import CountryCode


class Country(ORMSchema):
    country: str
    code: Optional[CountryCode] = None
