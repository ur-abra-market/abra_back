from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .company import Company
    from .country import Country


class CompanyPhone(ORMSchema):
    phone_number: Optional[str] = None
    company: Optional[Company] = None
    country: Optional[Country] = None
