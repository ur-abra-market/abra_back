from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from .core import ORMSchema

if TYPE_CHECKING:
    from .company import Company


class CompanyImage(ORMSchema):
    url: Optional[str] = None
    company: Optional[Company] = None
