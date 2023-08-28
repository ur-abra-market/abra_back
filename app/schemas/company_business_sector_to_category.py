from __future__ import annotations

from .core import ORMSchema


class CompanyBusinessSectorToCategory(ORMSchema):
    company_id: int
    category_id: int
