from __future__ import annotations

from ...schema import ApplicationSchema, BaseJsonSchema


class SupplierData(BaseJsonSchema, ApplicationSchema):
    license_number: str
