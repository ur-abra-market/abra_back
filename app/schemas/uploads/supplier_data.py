from __future__ import annotations

from ..schema import ApplicationSchema


class SupplierDataUpload(ApplicationSchema):
    license_number: str
