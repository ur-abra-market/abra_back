from __future__ import annotations

from typing import Optional

from .core import ORMSchema


class CompanyImage(ORMSchema):
    url: Optional[str] = None
    order: int
