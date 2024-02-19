from __future__ import annotations

from ..schema import ApplicationSchema


class PropertyValueUpload(ApplicationSchema):
    property_type_id: int
    property_value_id: int
    optional_value: str