from __future__ import annotations

from pydantic import BaseModel


class CompanyIDMixin(BaseModel):
    company_id: int
