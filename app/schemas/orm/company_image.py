from __future__ import annotations

from typing import Optional

from .schema import ORMSchema


class CompanyImage(ORMSchema):
    company_id: int
    url: Optional[str] = None
    serial_number: int
