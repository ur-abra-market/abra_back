from __future__ import annotations

from typing import Optional

from ...schema import ApplicationSchema


class SupplierDataUpdate(ApplicationSchema):
    license_number: Optional[str] = None
