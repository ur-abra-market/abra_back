from __future__ import annotations

from utils.pydantic import BaseJSONSchema

from ..schema import ApplicationSchema


class SupplierDataUpload(BaseJSONSchema, ApplicationSchema):
    license_number: str
