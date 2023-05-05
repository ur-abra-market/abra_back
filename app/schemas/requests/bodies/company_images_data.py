from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class CompanyImageData(ApplicationSchema):
    url: Optional[str] = None
