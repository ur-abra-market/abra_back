from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .country import Country


class CountryCode(ORMSchema):
    code: str
    country: Optional[Country] = None
