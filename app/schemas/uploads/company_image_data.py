from __future__ import annotations

from typing import Optional

from ..schema import ApplicationSchema


class CompanyImageDataUpload(ApplicationSchema):
    url: Optional[str] = None
